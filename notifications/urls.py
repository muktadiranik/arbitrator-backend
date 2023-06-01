from django.urls import path
from .views import NotificationsViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', NotificationsViewset, basename='notifications')
urlpatterns = router.urls
