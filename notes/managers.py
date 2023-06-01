from django.contrib.contenttypes.models import ContentType
from django.db import models


class NoteManager(models.Manager):
    def get_notes_for(self, app_label, model_class, obj_id, filters=None):
        filters = filters or {}  # dictionary of keyword arguments for django queryset filtering
        content_type = ContentType.objects.get(app_label=app_label, model=model_class)
        return super().get_queryset().filter(content_type=content_type, object_id=obj_id, **filters)

    def create_note_for(self, *args, **kwargs):
        if kwargs.get('app_label'):
            app_label = kwargs.pop('app_label')
            model_class = kwargs.pop('model_class')
            kwargs['object_id'] = kwargs.pop('obj_id')
            kwargs['content_type'] = ContentType.objects.get(app_label=app_label, model=model_class)
            return super().create(*args, **kwargs)

        raise KeyError('No app_label key provided in the request')
