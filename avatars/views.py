from rest_framework import viewsets, generics, permissions
from .models import Profile
from .serializers import ProfileSerializer, UserCreateSerializer
from .permissions import IsOwnerOrReadOnly


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
    permission_classes = [permissions.AllowAny] # Разрешаем доступ всем
