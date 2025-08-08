from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import phonenumbers
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
import uuid
from datetime import timedelta
from django_countries.fields import CountryField
from datetime import datetime
from storages.backends.s3boto3 import S3Boto3Storage
# Create your models here.

def validate_integer(value):
    try:
        if not isinstance(int(value), int):
            raise ValidationError("This field must be an integer")
    except (ValueError, TypeError):
        raise ValidationError("This field must be an integer")
    
def validate_string(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("This field must be a non-empty string")

def validate_phone(value):
    if not value:
        return  # Allow empty if the field is optional

    raw_value = str(value).strip()

    # Requerir que empiece con +
    if not raw_value.startswith("+"):
        raise ValidationError("Include country code (e.g., +31).")

    try:
        phone_number = phonenumbers.parse(raw_value, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError("Invalid phone number. Use format +[country code][number].")

    if not phonenumbers.is_valid_number(phone_number):
        raise ValidationError("The phone number entered is not valid.")

    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)

CURRENCY_CHOICES = [
    ('USD', 'USD'),
    ('EUR', 'EUR'),

]

class AuthorizedEmail(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)

class CVStorage(S3Boto3Storage):
    default_acl = 'private'  # o 'public-read'

def cv_upload_path(instance, filename):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"cvs/{instance.user.id}/{timestamp}.pdf"  # ya no pones 'cvs/' porque lo pone storage


class DeveloperProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    consent_promotional_use = models.BooleanField(null=True, blank=True)
    consent_given_at = models.DateTimeField(null=True, blank=True)

    # ---- Archivo CV y texto original extraído ---- (CV file and original extracted text)
    cv_file = models.FileField(upload_to=cv_upload_path, blank=False, null=False, storage=CVStorage())
    cv_raw_text = models.TextField(blank=True, null=True)

    # ---- Educación ---- (Education)
    university_education = models.JSONField(blank=True, null=True, default=None)
    education_certificates = models.JSONField(blank=True, null=True, default=None)

    # ---- Experiencia y proyectos ---- (Experience and projects)
    relevant_years_of_experience = models.IntegerField(blank=True, null=True)
    experience = models.JSONField(blank=True, null=True, default=None)
    projects = models.JSONField(blank=True, null=True, default=None)
    volunteering = models.JSONField(blank=True, null=True, default=None)

    # ---- Intereses y habilidades blandas ---- (Soft skills)
    interests = models.JSONField(blank=True, null=True, default=None)
    languages_spoken = models.JSONField(blank=True, null=True, default=None)  # Idiomas humanos (Inglés, Español)

    # ---- Technical skills classified (extracted by AI and validated by Pydantic) ----
    programming_languages = models.JSONField(blank=True, null=True, default=None)   # Ej: ["Python", "Swift"]
    frameworks_libraries = models.JSONField(blank=True, null=True, default=None)    # Ej: ["Django", "React"]
    architectures_patterns = models.JSONField(blank=True, null=True, default=None)  # Ej: ["MVVM", "Clean Architecture"]
    tools_version_control = models.JSONField(blank=True, null=True, default=None)   # Ej: ["Git", "Docker"]
    databases = models.JSONField(blank=True, null=True, default=None)               # Ej: ["PostgreSQL", "MongoDB"]
    cloud_platforms = models.JSONField(blank=True, null=True, default=None)         # Ej: ["AWS", "GCP"]
    testing_qa = models.JSONField(blank=True, null=True, default=None)              # Ej: ["Pytest", "Selenium"]
    devops_ci_cd = models.JSONField(blank=True, null=True, default=None)            # Ej: ["Jenkins", "GitHub Actions"]
    containerization = models.JSONField(blank=True, null=True, default=None)        # Ej: ["Docker", "Kubernetes"]
    data_skills = models.JSONField(blank=True, null=True, default=None)          # Ej: ["Pandas", "TensorFlow"]
    frontend_technologies = models.JSONField(blank=True, null=True, default=None)   # Ej: ["HTML", "CSS", "Tailwind"]
    mobile_development = models.JSONField(blank=True, null=True, default=None)      # Ej: ["SwiftUI", "Flutter"]
    apis_integrations = models.JSONField(blank=True, null=True, default=None)       # Ej: ["REST", "GraphQL"]
    security = models.JSONField(blank=True, null=True, default=None)                # Ej: ["JWT", "OAuth2"]
    agile_pm = models.JSONField(blank=True, null=True, default=None)                # Ej: ["Scrum", "Kanban"]
    operating_systems = models.JSONField(blank=True, null=True, default=None)       # Ej: ["Linux", "macOS"]

    # ---- Datos generales ---- (General data)
    main_developer_role = models.CharField(max_length=100, blank=True)
    country_living_in = CountryField(blank=True)
    nationality = CountryField(blank=True)
    telephone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone])
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    personal_website = models.URLField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Metadata (CV)
    cv_original_name = models.CharField(max_length=255, blank=True, null=True)
    cv_size = models.PositiveIntegerField(blank=True, null=True)  # en bytes
    cv_uploaded_at = models.DateTimeField(auto_now_add=True)

    # ---- Control de versiones del esquema ---- (Schema version control)
    schema_version = models.CharField(max_length=20, default="v1")

    def __str__(self):
        return self.user.username
        

"""
class MagicToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField()  # Siempre requerido
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)  # De un solo uso

    def is_valid(self):
        expiration_period = timedelta(days=7)  # 7 días de validez
        return not self.used and timezone.now() - self.created_at < expiration_period

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])
"""