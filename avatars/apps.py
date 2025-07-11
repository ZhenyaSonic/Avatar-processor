from django.apps import AppConfig


class AvatarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'avatars'

    def ready(self):
        # Импортируем сигналы, чтобы они были зарегистрированы при запуске Django
        import avatars.signals
