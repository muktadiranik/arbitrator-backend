from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('job-details', views.JobDetailViewset)
router.register('job-openings', views.OpeningViewset)
router.register('job-applications', views.JobApplicationViewset)
router.register('experiences', views.ExperienceViewset)

urlpatterns = router.urls
