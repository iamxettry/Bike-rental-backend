from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    label = 'authentication'


    def ready(self):
        import apps.auth.signals  # Import signals
        super().ready()  # Call the parent class's ready method
