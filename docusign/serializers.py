from rest_framework import serializers
from .models import DocuSignEnvelope


class EnvelopSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocuSignEnvelope
        fields = ['dispute', 'envelope_id', 'created_at', 'updated_at']
