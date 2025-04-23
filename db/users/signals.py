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
                # Valores predeterminados para campos obligatorios (NOT NULL)
                bachelor="Por completar",
                university_bachelor="Por completar",
                master="Por completar",
                university_master="Por completar",
                years_of_experience=1,  # Cumple con MinValueValidator(1)
                skills="Por completar",
                projects="Por completar",
                location="Por completar"
                # 'summary' puede estar en blanco
                # 'image' tiene valor predeterminado y permite nulos/blancos
            )

# NO incluimos la función save_profile aquí

