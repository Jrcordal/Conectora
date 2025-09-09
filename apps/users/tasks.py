from celery import shared_task
import logging
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from apps.users.models import CustomUser
from pydantic import BaseModel, EmailStr
from datetime import datetime
from django.conf import settings
from pydantic import ValidationError

import boto3
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from apps.users.models import UploadFile
from apps.developers.tasks import DeveloperFields, load_cv_from_s3
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)

from apps.developers.models import DeveloperProfile

def ensure_developer_profile(user):
    if getattr(user, "role", "").lower() != "developer":
        return None, False, "not_developer"

    with transaction.atomic():
        profile, created = DeveloperProfile.objects.get_or_create(
            user=user,
            defaults={
                "consent_promotional_use": True,
                "consent_given_at": timezone.now(),
                "is_open_to_work": True,
                "is_open_to_teach": True,
            },
        )
    return profile, created, "created" if created else "already_exists"




@shared_task(bind=True, autoretry_for=(IntegrityError,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def create_missing_developer_profiles(self, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist:
        logger.warning(f"[create_missing_developer_profiles] user_id={user_id} not found")
        return {"created": False, "reason": "user_not_found"}

    profile, created, reason = ensure_developer_profile(user)

    if profile is None:
        logger.info(f"[create_missing_developer_profiles] user_id={user_id} is not developer")
        return {"created": False, "reason": reason}

    logger.info(f"[create_missing_developer_profiles] user_id={user_id} "
                f"{'created profile' if created else 'profile already exists'} (pk={profile.pk})")
    return {"created": created, "username": user.username, "profile_pk": profile.pk, "reason": reason}



from enum import Enum

class TimezoneEnum(str, Enum):
    UTC_MINUS_12 = "UTC-12:00"
    UTC_MINUS_11 = "UTC-11:00"
    UTC_MINUS_10 = "UTC-10:00"
    UTC_MINUS_09 = "UTC-09:00"
    UTC_MINUS_08 = "UTC-08:00"
    UTC_MINUS_07 = "UTC-07:00"
    UTC_MINUS_06 = "UTC-06:00"
    UTC_MINUS_05 = "UTC-05:00"
    UTC_MINUS_04 = "UTC-04:00"
    UTC_MINUS_03 = "UTC-03:00"
    UTC_MINUS_02 = "UTC-02:00"
    UTC_MINUS_01 = "UTC-01:00"
    UTC_PLUS_00  = "UTC+00:00"
    UTC_PLUS_01  = "UTC+01:00"
    UTC_PLUS_02  = "UTC+02:00"
    UTC_PLUS_03  = "UTC+03:00"
    UTC_PLUS_04  = "UTC+04:00"
    UTC_PLUS_05  = "UTC+05:00"
    UTC_PLUS_06  = "UTC+06:00"
    UTC_PLUS_07  = "UTC+07:00"
    UTC_PLUS_08  = "UTC+08:00"
    UTC_PLUS_09  = "UTC+09:00"
    UTC_PLUS_10  = "UTC+10:00"
    UTC_PLUS_11  = "UTC+11:00"
    UTC_PLUS_12  = "UTC+12:00"


class UserFields(BaseModel):
    username: EmailStr
    email: EmailStr
    first_name: str =""
    last_name: str=""
    timezone: TimezoneEnum = TimezoneEnum.UTC_PLUS_02


class CustomUserAndProfileBootstrapped(BaseModel):
    user: UserFields
    developer_profile: DeveloperFields





def parse_cv_with_llm(text_cv,filename):
     # Preparar el prompt
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a software requirements analyst and project manager with a deep knowledge of the IT field and hiring process."),
            ("human", 
            """
        Based on the following CV, extract the information and structure it into the fields of a user and developer profile. Leave fields empty if no information is found. 

        - The username is the email.
        - Return the dates in the format YYYY-MM-DD. If no date day is present, assume the 1st day of the month. If the end date is the present day, output null.
        - Ignore Primary and Secondary school education for the university_education field and the education_certificates field.
        - Rephrase the descriptions of each field to make them comprehensive and clear.
        - Any information in a language other than English should be translated to English first.
        

        CV:
        {text_cv}
        """)
        ])

        prompt_input = chat_prompt.format(text_cv=text_cv)
        
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
            llm_structured = llm_01_temperature.with_structured_output(CustomUserAndProfileBootstrapped)
            
            logger.info("Calling LLM for structured output...")
            response = llm_structured.invoke(prompt_input)
            logger.info(f"LLM raw output (filename={filename}): {response}")

            parsed_response = response.model_dump()
            logger.info(f"Parsed response keys: {list(parsed_response.keys())}")

            return parsed_response
        except ValidationError as ve:
            raise
        except Exception as e:
            raise


def update_profile_fields(profile,parsed_response):
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
                
        except Exception as e:
            logger.error(f"Error saving profile to database: {str(e)}")
            raise

        return f"Profile {profile.user.email} processed successfully"




@shared_task(bind=True)
def create_user_and_devprofile_from_cv(self, batch_id: int, uf_id: int):
    logger.info(f"User creation from {batch_id} started for CV {uf_id}")
    uploaded_cv = UploadFile.objects.select_related("batch").get(id=uf_id)
    batch = uploaded_cv.batch
    s3_key = uploaded_cv.file.name
    bucket = settings.AWS_STORAGE_BUCKET_NAME
        
    logger.info(f"Loading CV from S3: bucket={bucket}, key={s3_key}")
        
    # Verificar configuración de S3
    if not settings.USE_S3:
        logger.error("USE_S3 is False - S3 storage not enabled")
        raise ValueError("S3 storage not enabled")
        
    if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, bucket]):
        logger.error("Missing AWS configuration")
        raise ValueError("Missing AWS configuration")

    text_cv = load_cv_from_s3(bucket, s3_key)
    filename =s3_key

    try:
        parsed = parse_cv_with_llm(text_cv, filename)

        # Acceso a los datos ya parseados
        # --- 1) Extraer datos del user ---
        user_block = parsed.get("user", {})
        email = (user_block.get("email") or "").strip().lower()
        # vacío
        if not email:
            uploaded_cv.status = "error"
            uploaded_cv.error_code = "no_email_extracted"
            uploaded_cv.error_message = "LLM did not return a valid email."
            uploaded_cv.save(update_fields=["status","error_code","error_message"])
            logger.warning(f"[batch={batch.id} uf={uf_id}] No email in {filename}")
            return {"status":"error","error_code":"no_email_extracted","uf_id": uf_id}

        # formato inválido
        try:
            validate_email(email)
        except DjangoValidationError as _e:
            uploaded_cv.status = "error"
            uploaded_cv.error_code = "invalid_email_format"
            uploaded_cv.error_message = f"Invalid email: {email}"
            uploaded_cv.save(update_fields=["status","error_code","error_message"])
            logger.warning(f"[batch={batch.id} uf={uf_id}] Invalid email '{email}' in {filename}")
            return {"status":"error","error_code":"invalid_email_format","uf_id": uf_id}


        first_name = (user_block.get("first_name") or "").strip()
        last_name = (user_block.get("last_name") or "").strip()
        timezone_val = user_block.get("timezone") or TimezoneEnum.UTC_PLUS_02
        if CustomUser.objects.filter(email=email).exists():
            uploaded_cv.status = "error"
            uploaded_cv.error_code = "email_already_registered"
            uploaded_cv.save(update_fields=["status", "error_code"])
            logger.error(f"Email already registered: {email} (batch {batch.id})")
            return {"status": "skipped", "reason": "email_exists", "email": email, "uf_id": uf_id}

        try:
            with transaction.atomic():
                user, created = CustomUser.objects.get_or_create(
                    email=email,
                    defaults=dict(
                        username=email,
                        first_name=first_name,
                        last_name=last_name,
                        timezone=timezone_val,
                        role="developer",
                        is_active=True,
                    )
                )
                if not created:
                    # Carrera: alguien lo insertó en medio → política: SKIP
                    uploaded_cv.status = "skipped"
                    uploaded_cv.error_code = "email_race_condition_exists_now"
                    uploaded_cv.error_message = "User appeared during creation window; no updates performed."
                    uploaded_cv.save(update_fields=["status", "error_code", "error_message"])
                    logger.info(f"[batch={batch.id} uf={uf_id}] Race condition: {email}. Skipping.")
                    return {"status": "skipped", "reason": "race_email_exists", "email": email, "uf_id": uf_id}

                logger.info(f"CustomUser created (id={user.id}, email={email})")

                # Perfil developer y update de campos del perfil
                profile, prof_created, reason = ensure_developer_profile(user)
                if profile is None:
                    # No debería ocurrir si role="developer", pero por si acaso:
                    uploaded_cv.status = "error"
                    uploaded_cv.error_code = f"cannot_create_profile:{reason}"
                    uploaded_cv.error_message = "ensure_developer_profile returned None."
                    uploaded_cv.save(update_fields=["status", "error_code", "error_message"])
                    logger.error(f"[batch={batch.id} uf={uf_id}] ensure_developer_profile failed for {email}: {reason}")
                    return {"status": "error", "error_code": "cannot_create_profile", "uf_id": uf_id}

                developer_profile_block = parsed.get("developer_profile", {}) or {}
                msg = update_profile_fields(profile, developer_profile_block)
                logger.info(msg)

        except IntegrityError as e:
            uploaded_cv.status = "error"
            uploaded_cv.error_code = "integrity_error"
            uploaded_cv.error_message = str(e)[:500]
            uploaded_cv.save(update_fields=["status", "error_code", "error_message"])
            logger.warning(f"[batch={batch.id} uf={uf_id}] IntegrityError for CV {filename}: {e}")
            return {"status": "error", "error_code": "integrity_error", "uf_id": uf_id}

        # 5) Éxito
        uploaded_cv.status = "processed"
        uploaded_cv.save(update_fields=["status"])
        logger.info(f"[batch={batch.id} uf={uf_id}] Processed OK for {email}")
        return {
            "status": "processed",
            "email": email,
            "user_id": user.id,
            "profile_id": profile.pk,
            "uf_id": uf_id,
        }

    except ValidationError as ve:
        uploaded_cv.status = "error"
        uploaded_cv.error_code = "validation_error"
        uploaded_cv.save(update_fields=["status", "error_code"])
        logger.error(f"ValidationError parsing CV {filename} (batch {batch.id}): {ve}")

    except Exception as e:
        uploaded_cv.status = "error"
        uploaded_cv.error_code = "unexpected_error"
        uploaded_cv.save(update_fields=["status", "error_code"])
        logger.exception(f"Unexpected error for CV {filename} (batch {batch.id}): {e}")

