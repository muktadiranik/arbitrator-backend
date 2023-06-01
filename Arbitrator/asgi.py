from django.core.asgi import get_asgi_application
from django.urls import re_path
django_asgi_app = get_asgi_application()
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Arbitrator.settings.dev')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns + [re_path(r"", django_asgi_app)]
        )
    ),
})
