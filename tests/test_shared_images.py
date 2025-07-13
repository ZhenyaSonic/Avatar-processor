from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from io import BytesIO
from PIL import Image
from avatars.models import SharedImage


class SharedImageAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='p')
        self.user2 = User.objects.create_user(username='user2', password='p')
        self.user3 = User.objects.create_user(username='user3', password='p')

        # Получаем токены
        self.token1 = self._get_token('user1', 'p')
        self.token2 = self._get_token('user2', 'p')

        # Готовим тестовое изображение
        img_bytes = BytesIO()
        Image.new('RGB', (100, 100), 'red').save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        self.test_image = SimpleUploadedFile("shared.jpg", img_bytes.read(), "image/jpeg")

    def _get_token(self, username, password):
        resp = self.client.post('/api/token/', {'username': username, 'password': password})
        return resp.data['access']

    def test_create_shared_image(self):
        """Тест загрузки изображения и "расшаривания" его для user2."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        data = {
            'caption': 'My first shared photo!',
            'image': self.test_image,
            'shared_with': [self.user2.id] # Делимся с user2
        }
        response = self.client.post('/api/shared_images/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SharedImage.objects.count(), 1)
        self.assertEqual(response.data['caption'], 'My first shared photo!')
        self.assertIn(self.user2.id, response.data['shared_with'])

    def test_recipient_can_view_image(self):
        """Тест: user2 (получатель) может видеть изображение, которым с ним поделился user1."""
        # user1 создает изображение и делится с user2
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.post('/api/shared_images/', {'image': self.test_image, 'shared_with': [self.user2.id]}, format='multipart')
        image_id = response.data['id']

        # user2 пытается посмотреть это изображение
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response = self.client.get(f'/api/shared_images/{image_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_view_image(self):
        """Тест: user3 (посторонний) не может видеть приватное изображение."""
        # user1 создает изображение, но НЕ делится с user3
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.post('/api/shared_images/', {'image': self.test_image, 'shared_with': [self.user2.id]}, format='multipart')
        image_id = response.data['id']

        # user3 пытается посмотреть
        token3 = self._get_token('user3', 'p')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token3}')
        response = self.client.get(f'/api/shared_images/{image_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # 404, т.к. queryset его не находит

    def test_owner_can_delete_image(self):
        """Тест: user1 (владелец) может удалить свое изображение."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.post('/api/shared_images/', {'image': self.test_image}, format='multipart')
        image_id = response.data['id']

        delete_response = self.client.delete(f'/api/shared_images/{image_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SharedImage.objects.count(), 0)

    def test_recipient_cannot_delete_image(self):
        """Тест: user2 (получатель) не может удалить чужое изображение."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.post('/api/shared_images/', {'image': self.test_image, 'shared_with': [self.user2.id]}, format='multipart')
        image_id = response.data['id']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        delete_response = self.client.delete(f'/api/shared_images/{image_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
