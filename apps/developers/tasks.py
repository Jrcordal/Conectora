from celery import shared_task
from django.conf import settings
from apps.developers.models import DeveloperProfile
import boto3
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import S3FileLoader
import os
from pydantic import BaseModel, Field
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class university_fields(BaseModel):
    university: str = Field(description="Name of the university")
    degree: str = Field(description="Degree obtained")
    degree_type: str = Field(description="Type of degree (Bsc, Msc, PhD, etc.)")
    start_date: datetime = Field(description="Start date of the degree")
    end_date: datetime = Field(description="End date of the degree")
    description: str = Field(description="Description of the degree")

class education_certificates_fields(BaseModel):
    certificate_name: str = Field(description="Name of the certificate")
    certificate_type: str = Field(description="Type of certificate (Certification, Diploma, etc.)")
    start_date: datetime = Field(description="Start date of the certificate")
    end_date: datetime = Field(description="End date of the certificate")
    description: str = Field(description="Description of the certificate")

class experience_fields(BaseModel):
    company_name: str = Field(description="Name of the company")
    job_title: str = Field(description="Job title")
    start_date: datetime = Field(description="Start date of the job")
    end_date: datetime = Field(description="End date of the job")
    description: str = Field(description="Description of the job")
    technologies_used: list[str] = Field(description="List of technologies or tech stack used in the job")

class project_fields(BaseModel):
    project_name: str = Field(description="Name of the project")
    start_date: datetime = Field(description="Start date of the project")
    end_date: datetime = Field(description="End date of the project")
    description: str = Field(description="Description of the project")
    technologies_used: list[str] = Field(description="List of technologies or tech stack used in the project")

class volunteering_fields(BaseModel):
    organization_name: str = Field(description="Name of the organization")
    start_date: datetime = Field(description="Start date of the volunteering")
    end_date: datetime = Field(description="End date of the volunteering")
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




@shared_task
def fill_developer_fields(profile_id):
    from apps.developers.models import DeveloperProfile

    profile = DeveloperProfile.objects.get(user_id=profile_id)
    s3_key = profile.cv_file.name
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    loader = S3FileLoader(
        bucket,
        s3_key,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    docs = loader.load()
    cv_text = docs[0].page_content
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a software requirements analyst and project manager with a deep knowledge of the IT field and hiring process."),
        ("human", 
        """
    Based on the following CV, extract the information and structure it into the fields of a developer profile. Leave fields empty if no information is found.

    DRAFT:
    {draft_text}
    """)
    ])


    prompt_input = chat_prompt.format(draft_text=cv_text)
    llm_01_temperature = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key = settings.GOOGLE_API_KEY
    )

    # Bind SoftwareRequirements schema as a tool to the model
    llm_structured = llm_01_temperature.with_structured_output(DeveloperFields)

    response = llm_structured.invoke(prompt_input)

    parsed_response = response.model_dump()

    profile.university_education = parsed_response['university_education']
    profile.education_certificates = parsed_response['education_certificates']
    profile.relevant_years_of_experience = parsed_response['relevant_years_of_experience']
    profile.experience = parsed_response['experience']
    profile.projects = parsed_response['projects']
    profile.volunteering = parsed_response['volunteering']
    profile.interests = parsed_response['interests']
    profile.languages_spoken = parsed_response['languages_spoken']
    profile.programming_languages = parsed_response['programming_languages']
    profile.frameworks_libraries = parsed_response['frameworks_libraries']
    profile.architectures_patterns = parsed_response['architectures_patterns']
    profile.tools_version_control = parsed_response['tools_version_control']
    profile.databases = parsed_response['databases']
    profile.cloud_platforms = parsed_response['cloud_platforms']
    profile.testing_qa = parsed_response['testing_qa']
    profile.devops_ci_cd = parsed_response['devops_ci_cd']
    profile.containerization = parsed_response['containerization']
    profile.data_skills = parsed_response['data_skills']
    profile.frontend_technologies = parsed_response['frontend_technologies']
    profile.mobile_development = parsed_response['mobile_development']
    profile.apis_integrations = parsed_response['apis_integrations']
    profile.security = parsed_response['security']
    profile.agile_pm = parsed_response['agile_pm']
    profile.operating_systems = parsed_response['operating_systems']
    profile.main_developer_role = parsed_response['main_developer_role']

    if profile.country_living_in is None:
        profile.country_living_in = parsed_response['country_living_in']
    if profile.nationality is None:
        profile.nationality = parsed_response['nationality']
    if profile.telephone_number is None:
        profile.telephone_number = parsed_response['telephone_number']
    if profile.linkedin is None:
        profile.linkedin = parsed_response['linkedin']
    if profile.github is None:
        profile.github = parsed_response['github']
    if profile.personal_website is None:
        profile.personal_website = parsed_response['personal_website']
    
    profile.save()

    return 
