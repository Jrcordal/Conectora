from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
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
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'timezone', 'role']  # email NO va aquí
    objects = CustomUserManager()

    def __str__(self):
        return self.username










