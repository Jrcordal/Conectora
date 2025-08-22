from celery import shared_task
import logging
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from apps.users.models import CustomUser

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(IntegrityError,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def create_missing_developer_profiles(self, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist:
        logger.warning(f"[create_missing_developer_profiles] user_id={user_id} not found")
        return {"created": False, "reason": "user_not_found"}

    if getattr(user, "role", None) != "developer":
        logger.info(f"[create_missing_developer_profiles] user_id={user_id} is not developer")
        return {"created": False, "reason": "not_developer"}

    from apps.developers.models import DeveloperProfile

    try:
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
    except IntegrityError:
        profile = DeveloperProfile.objects.get(user=user)
        created = False

    # 🔑 Usa pk (o user_id)
    logger.info(
        f"[create_missing_developer_profiles] user_id={user_id} "
        f"{'created profile' if created else 'profile already exists'} (pk={profile.pk})"
    )
    return {"created": created, "username": user.username, "profile_pk": profile.pk, "reason": "created" if created else "already_exists"}
