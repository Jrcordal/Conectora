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

    summary = models.TextField(blank=True, null=True)
    bachelor = models.CharField(max_length=255, validators=[validate_string], null=True, blank=True)
    university_bachelor = models.CharField(max_length=255, validators=[validate_string], null=True, blank=True)
    master = models.CharField(max_length=255, validators=[validate_string], null=True, blank=True)
    university_master = models.CharField(max_length=255, validators=[validate_string], null=True, blank=True)
    years_of_experience = models.IntegerField(validators=[MinValueValidator(1), validate_integer], null=True, blank=True)
    skills = models.TextField(max_length=1000, null=True, blank=True)
    projects = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(default='profilepic.jpg', upload_to='profile_pictures', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
    



