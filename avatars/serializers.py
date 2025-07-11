from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User (только для чтения)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Profile."""
    user = UserSerializer(read_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'name', 'avatar']
        read_only_fields = ['user']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user
