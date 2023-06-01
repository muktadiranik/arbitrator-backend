from django.apps import AppConfig


class LitigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'litigation'

    def ready(self):
        import litigation.signals.handlers
