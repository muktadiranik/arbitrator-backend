from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from .models import Room


class ActivityStreamConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name
        if self.scope.get('user').is_authenticated:
            Room.add(self.room_name, self.scope.get('user'))
            async_to_sync(self.channel_layer.group_add)(
                self.room_name,
                self.channel_name
            )

            self.accept()
        else:
            self.close()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        if self.scope.get('user').is_authenticated:
            Room.remove_user(self.scope.get('user'), self.room_name)

    def notification(self, event):
        message = event['message']
        self.send(message)


def send_notification_message(user_id, message, group_name):
    room = Room.objects.get(room_name=group_name)
    connected_user = list(room.users.all().values_list('id', flat=True))
    channel_layer = get_channel_layer()
    if user_id in connected_user:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification',
                'message': message
            }
        )
        return True
    return False
