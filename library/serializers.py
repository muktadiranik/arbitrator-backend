from rest_framework import serializers
from .models import Clause, ClauseCategory, LibraryChecklistItem, Checklist, Firm, Folder, File, Document, \
    TermsheetChecklistItem, ChecklistCategory
from litigation.serializers import ProfileSerializer, DisputeSerializer
from rest_framework.fields import empty


class ClauseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClauseCategory
        fields = ['id', 'name']


class ChecklistCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistCategory
        fields = ['id', 'name']


class FirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = ['id', 'name']


class ClauseSerializer(serializers.ModelSerializer):
    category = ClauseCategorySerializer(read_only=True)
    firm = FirmSerializer(read_only=True)
    arbitrator = ProfileSerializer(read_only=True)

    class Meta:
        model = Clause
        fields = ['id', 'category', 'title', 'content', 'firm', 'sequence', 'type', 'arbitrator']


class ClauseCreateSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        actor_id = kwargs['context']['request'].user.actor.id
        data.update({"arbitrator": actor_id})
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = Clause
        fields = ['id', 'category', 'title', 'content', 'firm', 'sequence', 'type', 'arbitrator']


class LibraryChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryChecklistItem
        fields = ['id', 'checklist', 'comments', 'initials', 'due_date', 'text', 'sequence']


class TermsheetChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsheetChecklistItem
        fields = ['id', 'checklist', 'comments', 'initials', 'due_date', 'text', 'checked', 'sequence']


class ChecklistCreateSerializer(serializers.ModelSerializer):
    items = LibraryChecklistItemSerializer(many=True, read_only=True)
    termsheet_items = TermsheetChecklistItemSerializer(many=True, read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        actor_id = kwargs['context']['request'].user.actor.id
        data.update({"arbitrator": actor_id})
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = Checklist
        fields = ['id', 'name', 'items', 'termsheet_items', 'category', 'description', 'firm', 'sequence', 'type',
                  'arbitrator']


class ChecklistSerializer(serializers.ModelSerializer):
    arbitrator = ProfileSerializer(read_only=True)
    items = LibraryChecklistItemSerializer(many=True, read_only=True)
    termsheet_items = TermsheetChecklistItemSerializer(many=True, read_only=True)
    category = ClauseCategorySerializer(required=False)

    class Meta:
        model = Checklist
        fields = ['id', 'name', 'items', 'termsheet_items', 'category', 'description', 'firm', 'sequence', 'type',
                  'arbitrator']


class FileSerializer(serializers.ModelSerializer):
    fileUrl = serializers.SerializerMethodField(read_only=True)

    def get_fileUrl(self, obj):
        self.request = self.context['request']
        if obj.file:
            return self.request.build_absolute_uri(obj.file.url)
        else:
            return None

    class Meta:
        model = File
        fields = ['id', 'folder', 'file', 'extension', 'name', 'size', 'sequence', 'fileUrl']
        extra_kwargs = {
            'file': {'write_only': True},
        }


class FolderCreateSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        actor_id = kwargs['context']['request'].user.actor.id
        data.update({"arbitrator": actor_id})
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'relation', 'parent', 'firm', 'case', 'sequence', 'type',
                  'arbitrator']


class FolderSerializer(serializers.ModelSerializer):
    folders = serializers.SerializerMethodField()
    files = FileSerializer(many=True, read_only=True)
    arbitrator = ProfileSerializer(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['files'].context.update(self.context)

    def get_folders(self, obj):
        queryset = Folder.objects.filter(parent_id=obj.id)
        serialized_folders = FolderSerializer(queryset, many=True, context=self.context).data
        return serialized_folders

    class Meta:
        model = Folder
        fields = ['id', 'name', 'relation', 'parent', 'folders', 'files', 'firm', 'case', 'sequence', 'type',
                  'arbitrator']


class DocumentSerializer(serializers.ModelSerializer):
    dispute = DisputeSerializer(read_only=True)

    class Meta:
        model = Document
        fields = ('id', 'dispute', 'text', 'created_at')


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'dispute', 'text', 'created_at')
