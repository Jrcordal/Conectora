from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile_for_non_superuser(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente solo para usuarios nuevos que NO sean superusuarios.
    Proporciona valores predeterminados para los campos obligatorios del perfil.
    """
    # Solo actuar si es un usuario recién creado Y NO es un superusuario
    if created and not instance.is_superuser:
        try:
            # Doble comprobación: asegurarse de que el perfil no exista ya
            Profile.objects.get(user=instance)
        except Profile.DoesNotExist:
            # Crear el perfil con valores predeterminados si no existe
            Profile.objects.create(
                user=instance,
                # Usar listas vacías para los campos JSON
                university_education=[],
                education_certificates=[],
                experience=[],
                skills=[],
                projects=[],
                interests=[],
                volunteering=[],
                languages=[],
                # Valores predeterminados para campos regulares
                location="",
                linkedin="",
                github="",
                personal_website=""
            )

# NO incluimos la función save_profile aquí

