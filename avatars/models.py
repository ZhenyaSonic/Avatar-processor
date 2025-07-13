import os
import uuid
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from .utils import process_image
from .validators import validate_image_file_extension, validate_image_size


def get_avatar_upload_path(instance, filename):
    """
    Генерирует уникальный путь для аватара пользователя.
    Пример: avatars/user_1/f7b4c4ec-9d6a-4c2s-8f0d-2b3a6a1c8b7e.jpg
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return os.path.join('avatars', f'user_{instance.user.id}', new_filename)


def get_shared_image_upload_path(instance, filename):
    """
    Генерирует путь для общих изображений.
    Пример: shared/owner_1/f7b4c4ec-9d6a-4c2s-8f0d-2b3a6a1c8b7e.jpg
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return os.path.join('shared', f'owner_{instance.owner.id}', new_filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    # Имя можно убрать, если оно дублирует user.first_name, или оставить для никнейма
    name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to=get_avatar_upload_path,
        validators=[validate_image_file_extension, validate_image_size],
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # Логика обработки аватара при изменении
        if self._is_avatar_changed() and self.avatar:
            processed_buffer = process_image(self.avatar)
            if processed_buffer:
                original_filename = os.path.basename(self.avatar.name)
                self.avatar.file = ContentFile(
                    processed_buffer.read(),
                    name=original_filename
                )

        # Если имя не задано, используем username пользователя
        if not self.name:
            self.name = self.user.username

        super().save(*args, **kwargs)

    def _is_avatar_changed(self):
        if not self.pk: return True
        try:
            old_avatar = Profile.objects.get(pk=self.pk).avatar
        except Profile.DoesNotExist:
            return True
        return old_avatar != self.avatar

    def __str__(self):
        return f'Profile for {self.user.username}'


class SharedImage(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_images'
    )
    image = models.ImageField(
        upload_to=get_shared_image_upload_path,
        validators=[validate_image_file_extension, validate_image_size]
    )
    caption = models.CharField(max_length=255, blank=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_images',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image by {self.owner.username} shared with {self.shared_with.count()} user(s)"