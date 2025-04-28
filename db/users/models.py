from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import phonenumbers
from django.core.exceptions import ValidationError
from django.conf import settings
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

#def validate_phone(value):
#    try:
#        # First try with + format
#        phone_number = phonenumbers.parse(str(value))
#    except phonenumbers.phonenumberutil.NumberParseException:
#            raise ValidationError("Invalid phone number format. Please include country code (e.g. +31)")
#    
#    if not phonenumbers.is_valid_number(phone_number):
#        raise ValidationError("This is not a valid phone number")

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    # Fields that will store JSON data
    university_education = models.JSONField(blank=True, null=True, default=None)
    education_certificates = models.JSONField(blank=True, null=True, default=None)

    experience = models.JSONField(blank=True, null=True, default=None)
    skills = models.JSONField(blank=True, null=True, default=None)
    projects = models.JSONField(blank=True, null=True, default=None)
    interests = models.JSONField(blank=True, null=True, default=None)
    volunteering = models.JSONField(blank=True, null=True, default=None)
    languages = models.JSONField(blank=True, null=True, default=None)
    
    # Regular fields
    location = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    personal_website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username
        
