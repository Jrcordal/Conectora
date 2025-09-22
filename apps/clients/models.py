from django.db import models
from django.conf import settings
from apps.developers.models import validate_phone,CURRENCY_CHOICES

# Create your models here.
class AuthorizedClientEmail(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,related_name='clientprofile')
    telephone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone])
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    role_in_company = models.CharField(max_length=20, blanck = True)
    
    def __str__(self):
        return self.user.username