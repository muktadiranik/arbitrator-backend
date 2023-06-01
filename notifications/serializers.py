from rest_framework import serializers
from actstream.models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['actor_content_type', 'actor_object_id', 'actor', 'verb', 'description', 'target_content_type',
                  'target_object_id', 'target', 'action_object_content_type', 'action_object_object_id',
                  'action_object', 'timestamp', 'public', 'objects']
