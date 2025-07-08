import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image


class Profile(models.Model):
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/')

    def save(self, *args, **kwargs):
        # Если аватар был изменен, обрабатываем его перед сохранением
        if self.pk and self.avatar:
            try:
                # Получаем предыдущий объект, чтобы проверить изменился ли файл
                old_obj = Profile.objects.get(pk=self.pk)
                if old_obj.avatar == self.avatar:
                    # Файл не менялся, просто сохраняем модель
                    super().save(*args, **kwargs)
                    return
            except Profile.DoesNotExist:
                pass

        if self.avatar:
            # Открываем изображение
            pil_img = Image.open(self.avatar)

            # 1. Обрезка до квадрата (crop)
            width, height = pil_img.size
            if width != height:
                min_dim = min(width, height)
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = (width + min_dim) // 2
                bottom = (height + min_dim) // 2
                pil_img = pil_img.crop((left, top, right, bottom))

            # 2. Сжатие без заметной потери качества
            buffer = BytesIO()
            pil_img.save(buffer, format='JPEG', quality=85, optimize=True)

            # Получаем имя файла
            image_name = os.path.basename(self.avatar.name)

            # Заменяем исходный файл обработанным в памяти
            self.avatar.file = ContentFile(buffer.getvalue(), name=image_name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
