import boto3
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
import logging
from apps.developers.models import DeveloperProfile
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from apps.developers.tasks import DeveloperFields
from django.conf import settings
from celery import shared_task
from django.utils import timezone


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




@shared_task(bind=True)
def create_or_update_developer_profile(self, profile_id, cv_file):
    
    from apps.developers.models import DeveloperProfile
    from django.db import transaction
    
    try:
        logger.info(f"Task {self.request.id} started for profile {profile_id}")

        # Obtener el perfil con manejo de errores
        try:
            profile = DeveloperProfile.objects.get(user_id=profile_id)
            logger.info(f"Profile found for user_id {profile_id}")
        except DeveloperProfile.DoesNotExist:
            profile = DeveloperProfile.objects.create(user_id=profile_id)
            
        
        if request.method == 'POST':
            cv_file = request.FILES.get('cv_file')



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

                # Set default values
                profile.consent_promotional_use = True
                profile.consent_given_at = timezone.now()
                profile.is_open_to_work = True
                profile.is_open_to_teach = True

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
                profile.telephone_number = parsed_response.get('telephone_number', '')
                profile.linkedin = parsed_response.get('linkedin', '')
                profile.github = parsed_response.get('github', '')
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
