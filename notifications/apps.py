from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    def ready(self):
        from actstream import registry
        from litigation.models import Offer, Dispute
        registry.register(Offer)
        registry.register(Dispute)
        import notifications.signals.handlers