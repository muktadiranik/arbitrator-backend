from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from .models import *
from .filters import *


class ClauseCategoryViewset(ModelViewSet):
    serializer_class = ClauseCategorySerializer
    queryset = ClauseCategory.objects.all()


class ChecklistCategoryViewset(ModelViewSet):
    serializer_class = ChecklistCategorySerializer
    queryset = ChecklistCategory.objects.all()


class FirmViewset(ModelViewSet):
    serializer_class = FirmSerializer
    queryset = Firm.objects.all()


class ClauseViewset(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ClauseFilter
    search_fields = ['content']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClauseSerializer

        return ClauseCreateSerializer

    def get_queryset(self):
        return Clause.objects.filter(arbitrator__user_id=self.request.user.id)


class ChecklistViewset(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ChecklistFilter
    search_fields = ['=name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChecklistSerializer

        return ChecklistCreateSerializer

    def get_queryset(self):
        return Checklist.objects.filter(arbitrator__user_id=self.request.user.id)


class LibraryChecklistItemViewset(ModelViewSet):
    serializer_class = LibraryChecklistItemSerializer

    def create_checklist_item(self, checklist_id, items):
        checklist_item_objs = []
        checklist_items = LibraryChecklistItemSerializer(items, many=True)
        try:
            checklist = Checklist.objects.get(id=checklist_id)
        except ObjectDoesNotExist:
            raise ValidationError({"checklist": ["checklist with this id does not exist"]})
        for instance in checklist_items.instance:
            instance.update({"checklist": checklist})
            checklist_item_objs.append(LibraryChecklistItem(**instance))

        created_items = LibraryChecklistItem.objects.bulk_create(checklist_item_objs)
        return LibraryChecklistItemSerializer(created_items, many=True).data

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        checklist_id = request_data.pop('checklist')
        items = request_data.pop('checklist_items')
        created_items = self.create_checklist_item(checklist_id, items)
        return Response(data=created_items, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return LibraryChecklistItem.objects.filter(checklist__arbitrator__id=self.request.user.actor.id)


class TermsheetChecklistItemViewset(ModelViewSet):
    serializer_class = TermsheetChecklistItemSerializer

    def create_termsheet_checklist_item(self, checklist_id, items):
        termsheet_checklist_item_objs = []
        checklist_items = TermsheetChecklistItemSerializer(items, many=True)
        try:
            checklist = Checklist.objects.get(id=checklist_id)
        except ObjectDoesNotExist:
            raise ValidationError({"checklist": ["checklist with this id does not exist"]})
        for instance in checklist_items.instance:
            instance.update({"checklist": checklist})
            termsheet_checklist_item_objs.append(TermsheetChecklistItem(**instance))

        created_items = TermsheetChecklistItem.objects.bulk_create(termsheet_checklist_item_objs)
        return TermsheetChecklistItemSerializer(created_items, many=True).data

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        checklist_id = request_data.pop('checklist')
        items = request_data.pop('termsheet_checklist_items')
        created_items = self.create_termsheet_checklist_item(checklist_id, items)
        return Response(data=created_items, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return TermsheetChecklistItem.objects.filter(checklist__arbitrator__id=self.request.user.actor.id)


class FolderViewset(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FolderFilter

    @action(methods=['get'], detail=False, url_name='get-folders-hierarchy',
            url_path=r'get-folders-hierarchy', filter_backends=[DjangoFilterBackend], filterset_class=FolderFilter)
    def get_hierarchical_folders(self, request):
        folders = self.filter_queryset(self.get_queryset()).filter(relation='root',
                                                                   arbitrator_id=self.request.user.actor.id)
        serialized_folders = FolderSerializer(folders, many=True, context={'request': request})
        return Response(data=serialized_folders.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FolderSerializer

        return FolderCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        return Folder.objects.filter(arbitrator__user_id=self.request.user.id)


class FilesViewset(ModelViewSet):
    serializer_class = FileSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('folder',)

    def get_queryset(self):
        return File.objects.filter(folder__arbitrator__id=self.request.user.actor.id)


class DocumentViewset(ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentSerializer

        return DocumentCreateSerializer

    def get_queryset(self):
        return Document.objects.filter(dispute__arbitrator__id=self.request.user.actor.id)
