from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register('clause', ClauseViewset, basename='clause')
router.register('category', ClauseCategoryViewset, basename='category')
router.register('checklist-category', ChecklistCategoryViewset, basename='checklist-category')
router.register('checklists', ChecklistViewset, basename='checklist')
router.register('checklist-items', LibraryChecklistItemViewset, basename='checklist-items')
router.register('termsheet-checklist-items', TermsheetChecklistItemViewset, basename='termsheet-checklist-items')
router.register('firm', FirmViewset, basename='firm')
router.register('folder', FolderViewset, basename='folder')
router.register('files', FilesViewset, basename='files')
router.register('documents', DocumentViewset, basename='documents')

urlpatterns = router.urls
