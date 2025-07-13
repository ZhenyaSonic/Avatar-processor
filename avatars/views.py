from rest_framework import generics, permissions, viewsets

from .models import Profile, SharedImage
from .permissions import CanViewOrOwnerCanModify, IsOwnerOrReadOnly
from .serializers import ProfileSerializer, SharedImageSerializer, UserCreateSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования профилей пользователей.
    - list:     GET /api/profiles/
    - retrieve: GET /api/profiles/{id}/
    - update:   PUT /api/profiles/{id}/
    - partial_update: PATCH /api/profiles/{id}/
    """
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]

    # Переопределяем права доступа для list/retrieve, чтобы их могли видеть все
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()


class UserCreateAPIView(generics.CreateAPIView):
    """Эндпоинт для регистрации новых пользователей."""
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]  # Разрешаем доступ всем


class SharedImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обмена изображениями.
    - list:     GET /api/shared_images/ - получить список изображений, которыми поделились с вами
    - create:   POST /api/shared_images/ - загрузить и поделиться новым изображением
    - retrieve: GET /api/shared_images/{id}/ - посмотреть конкретное изображение
    - destroy:  DELETE /api/shared_images/{id}/ - удалить свое изображение
    """
    serializer_class = SharedImageSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOrOwnerCanModify]
    # Запрещаем методы PUT и PATCH
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Этот метод определяет, какие объекты будут видны пользователю.
        Пользователь видит:
        1. Изображения, которыми он владеет.
        2. Изображения, которыми с ним поделились.
        """
        user = self.request.user
        # Используем Q-объекты для сложной фильтрации (OR)
        from django.db.models import Q
        return SharedImage.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct().select_related('owner').prefetch_related('shared_with')
