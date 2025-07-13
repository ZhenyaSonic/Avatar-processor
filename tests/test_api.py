from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from avatars.models import Profile


class ProfileAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем двух пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123')
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123')
        # Profile создается автоматически через сигнал

        # Получаем JWT токен для user1
        response = self.client.post('/api/token/', {
            'username': 'user1',
            'password': 'password123'}, format='json')
        self.token1 = response.data['access']

        # Готовим тестовое изображение
        image_bytes = BytesIO()
        image = Image.new('RGB', (200, 300), 'blue')
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        self.test_image = SimpleUploadedFile("test_avatar.jpg",
                                             image_bytes.read(),
                                             content_type="image/jpeg")

    def test_list_profiles_unauthenticated(self):
        """Анонимный пользователь может просматривать список профилей."""
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_profile_unauthenticated(self):
        """Анонимный пользователь может просматривать конкретный профиль."""
        profile1_id = self.user1.profile.id
        response = self.client.get(f'/api/profiles/{profile1_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'user1')

    def test_update_own_profile(self):
        """Аутентифицированный пользователь может обновить свой профиль."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        profile1_id = self.user1.profile.id

        data = {
            'name': 'New Name 1',
            'avatar': self.test_image
        }
        response = self.client.patch(f'/api/profiles/{profile1_id}/',
                                     data,
                                     format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name 1')
        self.assertIsNotNone(response.data['avatar'])

        # Проверяем, что аватар обработан и сохранен в папку пользователя
        profile = Profile.objects.get(id=profile1_id)
        self.assertIn(f'user_{self.user1.id}', profile.avatar.name)

        # Проверяем, что изображение стало квадратным
        with profile.avatar.storage.open(profile.avatar.name) as f:
            img = Image.open(f)
            self.assertEqual(img.width, img.height)

    def test_update_other_user_profile_forbidden(self):
        """Пользователь не может обновить чужой профиль."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        profile2_id = self.user2.profile.id
        data = {'name': 'Forbidden Name'}
        response = self.client.patch(f'/api/profiles/{profile2_id}/',
                                     data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
