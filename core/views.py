from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from .serializers import UsersSerializer
from .models import User
from rest_framework import status


class AllUsers(ListAPIView):
    serializer_class = UsersSerializer
    user_model = get_user_model()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return Response(data={'message': 'you don"t have access rights to list all the user'},
                        status=status.HTTP_401_UNAUTHORIZED)
