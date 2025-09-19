from django.db import models

# Create your models here.
class AuthorizedClientEmail(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)