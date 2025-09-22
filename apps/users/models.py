from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from datetime import datetime


# Create your models here.
TIMEZONE_CHOICES = [
    ('UTC-12:00', 'UTC-12:00'),
    ('UTC-11:00', 'UTC-11:00'),
    ('UTC-10:00', 'UTC-10:00'),
    ('UTC-09:00', 'UTC-09:00'),
    ('UTC-08:00', 'UTC-08:00'),
    ('UTC-07:00', 'UTC-07:00'),
    ('UTC-06:00', 'UTC-06:00'),
    ('UTC-05:00', 'UTC-05:00'),
    ('UTC-04:00', 'UTC-04:00'),
    ('UTC-03:00', 'UTC-03:00'),
    ('UTC-02:00', 'UTC-02:00'),
    ('UTC-01:00', 'UTC-01:00'),
    ('UTC+00:00', 'UTC+00:00'),
    ('UTC+01:00', 'UTC+01:00'),
    ('UTC+02:00', 'UTC+02:00'),
    ('UTC+03:00', 'UTC+03:00'),
    ('UTC+04:00', 'UTC+04:00'),
    ('UTC+05:00', 'UTC+05:00'),
    ('UTC+06:00', 'UTC+06:00'),
    ('UTC+07:00', 'UTC+07:00'),
    ('UTC+08:00', 'UTC+08:00'),
    ('UTC+09:00', 'UTC+09:00'),
    ('UTC+10:00', 'UTC+10:00'),
    ('UTC+11:00', 'UTC+11:00'),
    ('UTC+12:00', 'UTC+12:00'),
]



ROLE_CHOICES = [
    ('developer', 'Developer'),
    ('client', 'Client'),
]



def cv_upload_path_batches(instance, filename):
    ext = filename.split('.')[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    if ext not in ['pdf', 'docx']:
        raise ValidationError("Only PDF and DOCX files are allowed.")

    # ejemplo: batches_cvs/batch_12/3_20250902-120312.pdf
    return f"batches_cvs/batch_{instance.batch.id}/{instance.number_file}/{timestamp}.{ext}"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False) # if email had another variable name, we would need to add EMAIL_FIELD to the correct email
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    timezone = models.CharField(max_length=30,blank=False ,choices=TIMEZONE_CHOICES)
    role = models.CharField(max_length=30,null=True ,choices=ROLE_CHOICES, blank=False)
    is_staff = models.BooleanField(default=False)
    is_agency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_bootstrapped = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'timezone', 'role']  # email NO va aquí
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    @property
    def has_profile(self) -> bool:
        # NO hace query si antes hiciste select_related('profile')
        return hasattr(self, 'devprofile')
    #@property
    #def is_client(self) -> bool:
    #    return hasattr(self,'clientprofile')



class UploadStatus(models.TextChoices):
    PENDING    = "pending",    "Pending"
    PROCESSING = "processing", "Processing"
    DONE       = "done",       "Done"
    SKIPPED    = "skipped",    "Skipped"   # <— NUEVO (lo usa tu task)
    ERROR      = "error",      "Error"

class UploadErrorCode(models.TextChoices):
    NONE                 = "",                        "-"
    NO_EMAIL_EXTRACTED   = "no_email_extracted",      "No email extracted"
    INVALID_EMAIL_FORMAT = "invalid_email_format",     "Invalid email format"
    EMAIL_ALREADY_EXISTS = "email_already_registered", "Email already registered"
    INTEGRITY_ERROR      = "integrity_error",          "Integrity error"
    VALIDATION_ERROR     = "validation_error",         "Validation error"
    UNEXPECTED_ERROR     = "unexpected_error",         "Unexpected error"

class UploadBatch(models.Model):
    created_by = models.ForeignKey("users.CustomUser", on_delete=models.PROTECT, related_name="upload_batches")
    created_at = models.DateTimeField(auto_now_add=True)
    total_files = models.PositiveIntegerField(default=0)
    processed_files = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Batch #{self.id}"

    # Actualiza para los nuevos códigos:
    @property
    def files_without_email(self):
        return self.files.filter(status=UploadStatus.ERROR, error_code=UploadErrorCode.NO_EMAIL_EXTRACTED)

    @property
    def files_with_existing_email(self):
        return self.files.filter(status__in=[UploadStatus.ERROR, UploadStatus.SKIPPED],
                                 error_code=UploadErrorCode.EMAIL_ALREADY_EXISTS)


class UploadFile(models.Model):
    STATUS = UploadStatus.choices

    batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=cv_upload_path_batches)
    created_at = models.DateTimeField(auto_now_add=True)
    number_file = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=12, choices=STATUS, default=UploadStatus.PENDING)
    error_code = models.CharField(max_length=64, blank=True, default=UploadErrorCode.NONE)
    error_message = models.TextField(blank=True, default="")  # <— NUEVO

    processing_started_at = models.DateTimeField(null=True, blank=True)  # <— NUEVO
    processed_at = models.DateTimeField(null=True, blank=True)           # <— NUEVO

    class Meta:
        indexes = [
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["status", "error_code"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            # Descomenta si quieres garantizar unicidad por batch+número
            models.UniqueConstraint(fields=["batch", "number_file"], name="uniq_batch_numberfile"),
        ]

    def mark_processing(self):
        self.status = UploadStatus.PROCESSING
        self.processing_started_at = timezone.now()
        self.error_code = UploadErrorCode.NONE
        self.error_message = ""
        self.save(update_fields=["status", "processing_started_at", "error_code", "error_message"])

    def mark_done(self):
        self.status = UploadStatus.DONE
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])

    def mark_skipped(self, code=UploadErrorCode.EMAIL_ALREADY_EXISTS, msg=""):
        self.status = UploadStatus.SKIPPED
        self.error_code = code
        self.error_message = msg
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "error_code", "error_message", "processed_at"])

    def mark_error(self, code, msg=""):
        self.status = UploadStatus.ERROR
        self.error_code = code
        self.error_message = msg[:500]
        self.save(update_fields=["status", "error_code", "error_message"])