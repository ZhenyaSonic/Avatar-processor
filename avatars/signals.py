from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    При создании нового пользователя (User) автоматически создает
    связанный с ним объект Profile.
    """
    if created:
        Profile.objects.create(user=instance)
