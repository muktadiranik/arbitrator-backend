from django.urls import path, include
from dj_rest_auth.urls import urlpatterns
from .views import *

urlpatterns += [
    path('users/', AllUsers.as_view(), name='all-users')
]
