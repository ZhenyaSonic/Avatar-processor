from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, SharedImage


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


class SharedImageSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    # Используем PrimaryKeyRelatedField для получения списка ID пользователей при создании/обновлении
    shared_with = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False  # Делаем поле необязательным
    )

    class Meta:
        model = SharedImage
        fields = [
            'id',
            'owner',
            'image',
            'caption',
            'shared_with',
            'created_at'
        ]
        read_only_fields = ['owner', 'created_at']

    def create(self, validated_data):
        # Устанавливаем текущего пользователя как владельца изображения
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
