from django.urls import re_path

from notifications.consumer import ActivityStreamConsumer

websocket_urlpatterns = [
    re_path(r'ws/notification/(?P<room_name>[\w-]+)/$', ActivityStreamConsumer.as_asgi()),


]
