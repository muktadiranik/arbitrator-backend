from django.contrib.auth import get_user_model
from django.db import models
from asgiref.sync import sync_to_async


class Room(models.Model):
    room_name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(get_user_model(), related_name='rooms')

    @classmethod
    def add(cls, room_name, user):
        room, created = cls.objects.get_or_create(room_name=room_name)
        room.users.add(user)
        return created

    @classmethod
    def remove_user(cls, user, room_name):
        room = cls.objects.get(room_name=room_name)
        if room:
            room.users.remove(user)
