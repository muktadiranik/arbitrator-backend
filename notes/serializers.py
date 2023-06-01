from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Note, Tag


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'label']


class NoteCreateSerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(write_only=True)
    model_class = serializers.CharField(write_only=True)
    obj_id = serializers.IntegerField(write_only=True)
    app = serializers.CharField(source='content_type.app_label', read_only=True)
    model = serializers.CharField(source='content_type.name', read_only=True)
    content_type = serializers.PrimaryKeyRelatedField(read_only=True)
    object_id = serializers.IntegerField(read_only=True)
    author = AuthorSerializer(read_only=True)

    def create(self, validated_data: dict) -> Note:
        validated_data['author_id'] = self.context['author_id']
        tags = validated_data.pop('tags')

        if tags:
            instance = Note.objects.create_note_for(**validated_data)
            instance.tags.add(*tags)
            return instance

        return Note.objects.create_note_for(**validated_data)

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'tags', 'author', 'app', 'model',
                  'content_type', 'object_id', 'app_label', 'model_class', 'obj_id', 'created_at']


class NoteUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance: Note, validated_data: dict) -> Note:
        if validated_data.get('tags'):
            tags = validated_data.pop('tags')
            instance = super().update(instance, validated_data)
            instance.tags.clear()
            instance.tags.add(*tags)
            return instance

        return super().update(instance, validated_data)

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'tags', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    app = serializers.ReadOnlyField(source='content_type.app_label')
    model = serializers.ReadOnlyField(source='content_type.name')
    tags = TagSerializer(many=True)
    author = AuthorSerializer()

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'content_type', 'app', 'model', 'object_id', 'tags', 'author']
