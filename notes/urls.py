from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tags', views.TagModelViewSet, basename='tags')
router.register('', views.NoteModelViewSet, basename='notes')

urlpatterns = router.urls
