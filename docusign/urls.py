from .views import *
from django.urls import path

urlpatterns = [
    path('handle-docusign/', HandleDocusignCallback.as_view(), name='handle-docusign')
]
