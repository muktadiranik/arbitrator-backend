from rest_framework.routers import DefaultRouter

from timelog.views import TimeLogViewSet

router = DefaultRouter()

router.register('entries', TimeLogViewSet, basename='timelogs')

urlpatterns = router.urls
