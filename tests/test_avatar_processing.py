from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from avatars.models import Profile
from PIL import Image
from io import BytesIO
import os


class AvatarProcessingTest(TestCase):

    def setUp(self):
        # Создаем "сырое" изображение в памяти (неквадратное)
        self.original_image_bytes = BytesIO()
        image = Image.new('RGB', (200, 300), 'blue') # Не квадрат
        image.save(self.original_image_bytes, format='JPEG')
        self.original_size = self.original_image_bytes.tell()
        self.original_image_bytes.seek(0)

        # Создаем объект SimpleUploadedFile для загрузки
        self.uploaded_file = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=self.original_image_bytes.read(),
            content_type='image/jpeg'
        )

    def test_avatar_processing_on_save(self):
        # 1. Создаем профиль и загружаем аватар
        profile = Profile.objects.create(
            name='Test User',
            avatar=self.uploaded_file
            )
        profile.save()

        # Обновляем объект из базы данных, чтобы получить путь к S3
        profile.refresh_from_db()

        # --- Проверки ---

        # Тест 1: Файл успешно лежит в S3 (хранилище)
        self.assertTrue(
            profile.avatar.storage.exists(profile.avatar.name),
            "Файл не найден в S3-хранилище."
            )

        # Тест 2: Изображение стало квадратным
        # Открываем файл из хранилища для проверки размеров
        with profile.avatar.storage.open(profile.avatar.name) as f:
            processed_image = Image.open(f)
            self.assertEqual(
                processed_image.width,
                processed_image.height,
                "Изображение не стало квадратным."
                )
            self.assertEqual(
                processed_image.width,
                200,
                "Размер квадрата неверный (ожидалось 200px)."
            )

        # Тест 3: Размер файла стал меньше
        processed_size = profile.avatar.size
        self.assertLess(
            processed_size, self.original_size,
            "Размер файла не уменьшился после сжатия."
            )

        # Очистка: удаляем файл из хранилища после теста
        profile.avatar.delete(save=False)
