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


class CanViewOrOwnerCanModify(permissions.BasePermission):
    """
    Право доступа для SharedImage:
    - Просмотр (GET) разрешен владельцу и пользователям из 'shared_with'.
    - Удаление (DELETE) разрешено только владельцу ('owner').
    - Создание (POST) разрешено любому аутентифицированному пользователю.
    - Изменение (PUT/PATCH) запрещено.
    """

    def has_permission(self, request, view):
        # Разрешаем создание (POST) и просмотр списка (GET) всем аутентифицированным пользователям
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли пользователь в списке получателей
        is_recipient = request.user in obj.shared_with.all()

        # Разрешаем GET-запросы владельцу ИЛИ получателю
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or is_recipient

        # Разрешаем DELETE-запросы только владельцу
        if request.method == 'DELETE':
            return obj.owner == request.user

        # Запрещаем все остальные методы (PUT, PATCH)
        return False
