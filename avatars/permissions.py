from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Кастомное право доступа:
    - Разрешает чтение (GET, HEAD, OPTIONS) любому запросу.
    - Разрешает запись (PUT, PATCH) только владельцу объекта.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем любые "безопасные" методы (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем запись только если пользователь является владельцем профиля
        return obj.user == request.user
