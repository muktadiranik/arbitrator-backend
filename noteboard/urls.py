from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register('lanes', LaneViewset, basename='lane')
router.register('notes', NoteViewset, basename='note')
urlpatterns = router.urls
