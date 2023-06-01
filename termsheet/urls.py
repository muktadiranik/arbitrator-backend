from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register('sheets', TermsheetViewset, 'termsheets')
router.register('sheet-titles', TermsheetTitleViewset, 'sheet-titles')
router.register('section-titles', SectionTitleViewset, 'section-titles')
router.register('digital-signatures', DigitalSignatureViewset, 'digital-signatures')
router.register('sheet-sections', TermsheetSectionViewset, 'sheet-sections')
urlpatterns = router.urls
