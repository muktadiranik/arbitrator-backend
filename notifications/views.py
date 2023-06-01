from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import ActionSerializer
from actstream.models import Action
from django.db.models import Q


class NotificationsViewset(ModelViewSet):
    http_method_names = ['get', 'patch']
    serializer_class = ActionSerializer
    queryset = Action.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('actor_object_id', 'target_object_id',)

    @action(methods=['get'], detail=False, url_name='get-unread-notifications',
            url_path=r'get-unread-notifications/(?P<user_id>[^/.]+)')
    def get_unread_notifications(self, request, user_id):
        unread_notifications = Action.objects.filter(Q(data__contains={"read": False}), actor_object_id=user_id)
        serialized_notifications = ActionSerializer(unread_notifications, many=True)
        return Response(data={'notifications': serialized_notifications.data}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='get-pending-notifications',
            url_path=r'get-pending-notifications/(?P<user_id>[^/.]+)')
    def get_pending_notifications(self, request, user_id):
        unread_notifications = Action.objects.filter(Q(data__contains={"sent": False}), actor_object_id=user_id)
        serialized_notifications = ActionSerializer(unread_notifications, many=True)
        return Response(data={'notifications': serialized_notifications.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.data['read'] = True
        notification.save()
        serialized_notification = ActionSerializer(notification)
        return Response(data=serialized_notification.data, status=status.HTTP_200_OK)
