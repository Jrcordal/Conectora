from celery import shared_task
from django.conf import settings
from apps.developers.models import DeveloperProfile
import boto3
import tempfile
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
#from langchain_community.document_loaders import S3FileLoader
import os
import tempfile
from pydantic import BaseModel, Field
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


import logging
logger = logging.getLogger(__name__)


def load_cv_from_s3(bucket: str, key: str):
    s3_client = boto3.client("s3")
    fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(key)[1])
    os.close(fd)
    s3_client.download_file(bucket, key, tmp_path)

    ext = tmp_path.lower().split(".")[-1]
    if ext == "pdf":
        docs = PyPDFLoader(tmp_path).load()
    elif ext == "docx":
        docs = Docx2txtLoader(tmp_path).load()
    else:
        raise ValueError(f"Unsupported format: {ext}")

    os.remove(tmp_path)
    return "\n\n".join(d.page_content for d in docs)


class university_fields(BaseModel):
    university: str = Field(description="Name of the university")
    degree: str = Field(description="Degree obtained")
    degree_type: str = Field(description="Type of degree (Bsc, Msc, PhD, etc.)")
    start_date: str = Field(description="Start date of the degree")
    end_date: str = Field(description="End date of the degree")
    description: str = Field(description="Description of the degree")

class education_certificates_fields(BaseModel):
    certificate_name: str = Field(description="Name of the certificate")
    certificate_type: str = Field(description="Type of certificate (Certification, Diploma, etc.)")
    start_date: str = Field(description="Start date of the certificate")
    end_date: str = Field(description="End date of the certificate")
    description: str = Field(description="Description of the certificate")

class experience_fields(BaseModel):
    company_name: str = Field(description="Name of the company")
    job_title: str = Field(description="Job title")
    start_date: str = Field(description="Start date of the job")
    end_date: str = Field(description="End date of the job")
    description: str = Field(description="Description of the job")
    technologies_used: list[str] = Field(description="List of technologies or tech stack used in the job")

class project_fields(BaseModel):
    project_name: str = Field(description="Name of the project")
    start_date: str = Field(description="Start date of the project")
    end_date: str = Field(description="End date of the project")
    description: str = Field(description="Description of the project")
    technologies_used: list[str] = Field(description="List of technologies or tech stack used in the project")

class volunteering_fields(BaseModel):
    organization_name: str = Field(description="Name of the organization")
    start_date: str = Field(description="Start date of the volunteering")
    end_date: str = Field(description="End date of the volunteering")
    description: str = Field(description="Description of the volunteering")

class DeveloperFields(BaseModel):
    # ---- Educación ---- (Education)
    university_education: list[university_fields] = Field(description="List of universities")
    education_certificates: list[education_certificates_fields] = Field(description="List of education certificates")

    # ---- Experiencia y proyectos ---- (Experience and projects)
    relevant_years_of_experience: int = Field(description="Number of years of experience since the first job in the field of IT")
    experience: list[experience_fields] = Field(description="List of relevant work/job experiences in IT")
    projects: list[project_fields] = Field(description="List of projects or side projects")
    volunteering: list[volunteering_fields] = Field(description="List of volunteering experiences")

    # ---- Intereses y habilidades blandas ---- (Soft skills)
    interests: list[str] = Field(description="List of interests")
    languages_spoken: list[str] = Field(description="List of languages spoken")  # Idiomas humanos (Inglés, Español)

    # ---- Technical skills classified (extracted by AI and validated by Pydantic) ----
    programming_languages: list[str] = Field(description="List of programming languages")    # Ej: ["Python", "Swift"]
    frameworks_libraries: list[str] = Field(description="List of frameworks and libraries")     # Ej: ["Django", "React"]
    architectures_patterns: list[str] = Field(description="List of architectures and patterns")   # Ej: ["MVVM", "Clean Architecture"]
    tools_version_control: list[str] = Field(description="List of version control tools")    # Ej: ["Git", "Docker"]
    databases: list[str] = Field(description="List of databases")               # Ej: ["PostgreSQL", "MongoDB"]
    cloud_platforms: list[str] = Field(description="List of cloud platforms")         # Ej: ["AWS", "GCP"]
    testing_qa: list[str] = Field(description="List of testing and QA tools")              # Ej: ["Pytest", "Selenium"]
    devops_ci_cd: list[str] = Field(description="List of devops and CI/CD tools")         # Ej: ["Jenkins", "GitHub Actions"]
    containerization: list[str] = Field(description="List of containerization tools")        # Ej: ["Docker", "Kubernetes"]
    data_skills: list[str] = Field(description="List of data skills")           # Ej: ["Pandas", "TensorFlow"]
    frontend_technologies: list[str] = Field(description="List of frontend technologies")   # Ej: ["HTML", "CSS", "Tailwind"]
    mobile_development: list[str] = Field(description="List of mobile development tools")      # Ej: ["SwiftUI", "Flutter"]
    apis_integrations: list[str] = Field(description="List of APIs and integrations")     # Ej: ["REST", "GraphQL"]
    security: list[str] = Field(description="List of security tools")                 # Ej: ["JWT", "OAuth2"]
    agile_pm: list[str] = Field(description="List of agile and PM tools")                 # Ej: ["Scrum", "Kanban"]
    operating_systems: list[str] = Field(description="List of operating systems")       # Ej: ["Linux", "macOS"]
        
    # ---- Datos generales ---- (General data)
    main_developer_role: str = Field(description="Main developer role, e.g. Backend Developer, Frontend Developer, Full Stack Developer, etc.")
    country_living_in: str = Field(description="Country living in, e.g. Spain")
    nationality: str = Field(description="Country of origin, e.g. Spain")
    telephone_number: str = Field(description="Telephone number, e.g. +34 666 666 666")
    linkedin: str = Field(description="Linkedin profile URL, e.g. https://www.linkedin.com/in/john-doe-1234567890/")
    github: str = Field(description="Github profile URL, e.g. https://github.com/john-doe")
    personal_website: str = Field(description="Personal website URL, e.g. https://www.john-doe.com")




@shared_task(bind=True)
def fill_developer_fields(self, profile_id):
    from apps.developers.models import DeveloperProfile
    from django.db import transaction
    
    try:
        logger.info(f"Task {self.request.id} started for profile {profile_id}")

        # Obtener el perfil con manejo de errores
        try:
            profile = DeveloperProfile.objects.get(user_id=profile_id)
            logger.info(f"Profile found for user_id {profile_id}")
        except DeveloperProfile.DoesNotExist:
            logger.error(f"DeveloperProfile not found for user_id {profile_id}")
            raise
        
        # Verificar que existe el archivo CV
        if not profile.cv_file:
            logger.error(f"No CV file found for profile {profile_id}")
            raise ValueError("No CV file found")
        
        s3_key = profile.cv_file.name
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        
        logger.info(f"Loading CV from S3: bucket={bucket}, key={s3_key}")
        
        # Verificar configuración de S3
        if not settings.USE_S3:
            logger.error("USE_S3 is False - S3 storage not enabled")
            raise ValueError("S3 storage not enabled")
        
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, bucket]):
            logger.error("Missing AWS configuration")
            raise ValueError("Missing AWS configuration")

        # Cargar el documento
        try:
            cv_text = load_cv_from_s3(bucket, s3_key)
            if not cv_text:
                logger.error("No documents loaded from S3")
                raise ValueError("No documents loaded from S3")
            
            if not cv_text.strip():
                logger.error("CV text is empty")
                raise ValueError("CV text is empty")
            
            logger.info(f"CV text loaded successfully, length: {len(cv_text)} characters")
        except Exception as e:
            logger.error(f"Error loading CV from S3: {str(e)}")
            raise
        
        # Preparar el prompt
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a software requirements analyst and project manager with a deep knowledge of the IT field and hiring process."),
            ("human", 
            """
        Based on the following CV, extract the information and structure it into the fields of a developer profile. Leave fields empty if no information is found. 

        - Return the dates in the format YYYY-MM-DD. If no date day is present, assume the 1st day of the month. If the end date is the present day, output null.
        - Ignore Primary and Secondary school education for the university_education field and the education_certificates field.
        - Rephrase the descriptions of each field to make them comprehensive and clear.
        

        DRAFT:
        {draft_text}
        """)
        ])

        prompt_input = chat_prompt.format(draft_text=cv_text)
        
        # Verificar API key de Google
        if not settings.GOOGLE_API_KEY:
            logger.error("Google API key not configured")
            raise ValueError("Google API key not configured")
        
        # Configurar LLM
        try:
            llm_01_temperature = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                google_api_key=settings.GOOGLE_API_KEY
            )

            # Bind schema as a tool to the model
            llm_structured = llm_01_temperature.with_structured_output(DeveloperFields)
            
            logger.info("Calling LLM for structured output...")
            response = llm_structured.invoke(prompt_input)
            logger.info(f"LLM raw output (profile_id={profile_id}): {response}")

            parsed_response = response.model_dump()
            logger.info(f"Parsed response keys: {list(parsed_response.keys())}")
            
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise

        # Guardar en la base de datos con transacción
        try:
            with transaction.atomic():
                # Campos de educación
                profile.university_education = parsed_response.get('university_education', [])
                profile.education_certificates = parsed_response.get('education_certificates', [])
                
                # Experiencia
                profile.relevant_years_of_experience = parsed_response.get('relevant_years_of_experience')
                profile.experience = parsed_response.get('experience', [])
                profile.projects = parsed_response.get('projects', [])
                profile.volunteering = parsed_response.get('volunteering', [])
                
                # Habilidades blandas
                profile.interests = parsed_response.get('interests', [])
                profile.languages_spoken = parsed_response.get('languages_spoken', [])
                
                # Habilidades técnicas
                profile.programming_languages = parsed_response.get('programming_languages', [])
                profile.frameworks_libraries = parsed_response.get('frameworks_libraries', [])
                profile.architectures_patterns = parsed_response.get('architectures_patterns', [])
                profile.tools_version_control = parsed_response.get('tools_version_control', [])
                profile.databases = parsed_response.get('databases', [])
                profile.cloud_platforms = parsed_response.get('cloud_platforms', [])
                profile.testing_qa = parsed_response.get('testing_qa', [])
                profile.devops_ci_cd = parsed_response.get('devops_ci_cd', [])
                profile.containerization = parsed_response.get('containerization', [])
                profile.data_skills = parsed_response.get('data_skills', [])
                profile.frontend_technologies = parsed_response.get('frontend_technologies', [])
                profile.mobile_development = parsed_response.get('mobile_development', [])
                profile.apis_integrations = parsed_response.get('apis_integrations', [])
                profile.security = parsed_response.get('security', [])
                profile.agile_pm = parsed_response.get('agile_pm', [])
                profile.operating_systems = parsed_response.get('operating_systems', [])
                
                # Datos generales
                profile.main_developer_role = parsed_response.get('main_developer_role', '')

                # Solo actualizar si están vacíos
                if not profile.telephone_number:
                    profile.telephone_number = parsed_response.get('telephone_number', '')
                if not profile.linkedin:
                    profile.linkedin = parsed_response.get('linkedin', '')
                if not profile.github:
                    profile.github = parsed_response.get('github', '')
                if not profile.personal_website:
                    profile.personal_website = parsed_response.get('personal_website', '')

                
                profile.save()
                logger.info(f"Profile {profile_id} updated successfully by task {self.request.id}")
                
        except Exception as e:
            logger.error(f"Error saving profile to database: {str(e)}")
            raise

        return f"Profile {profile_id} processed successfully"
        
    except Exception as e:
        logger.error(f"Task {self.request.id} failed for profile {profile_id}: {str(e)}")
        # Re-raise la excepción para que Celery la registre como fallida
        raise self.retry(exc=e, countdown=60, max_retries=3) 



