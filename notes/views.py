from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Note, Tag
from .serializers import TagSerializer, NoteSerializer, NoteCreateSerializer, NoteUpdateSerializer


class TagModelViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class NoteModelViewSet(ModelViewSet):
    queryset = Note.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['content']

    def get_serializer_context(self):
        return {'author_id': self.request.user.id}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NoteCreateSerializer

        elif self.request.method in ['PATCH', 'PUT']:
            return NoteUpdateSerializer

        return NoteSerializer

    def get_filters(self, filter_fields):
        filters = {}
        for field in filter_fields:
            value = self.request.query_params.get(field)
            if value:
                filters[field] = value
        return filters

    @action(methods=['get'], detail=False, url_name='object',
            url_path='object/(?P<app_label>[^/.]+)/(?P<model>[^/.]+)/(?P<obj_id>[^/.]+)')
    def get_notes_for_specific_object(self, request, app_label, model, obj_id):
        # Custom logic for filtering, passed as query params
        filter_fields = ['author']
        filters = self.get_filters(filter_fields)

        notes = Note.objects.get_notes_for(app_label, model, obj_id, filters=filters)
        serializer = NoteSerializer(notes, many=True)
        if serializer.data:
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(data=[], status=status.HTTP_200_OK)
