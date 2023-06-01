from rest_framework import serializers
from .models import *


class TermsheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermSheet
        fields = ['id', 'title', 'dispute']


class TermsheetTitleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='text')

    class Meta:
        model = TermsheetTitle
        fields = ['id', 'title']


class SectionTitleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='text')

    class Meta:
        model = SectionTitle
        fields = ['id', 'title']


class TermsheetSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsheetSection
        fields = ['id', 'termsheet', 'title', 'text', 'created_at', 'updated_at']


class DigitalSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalSignature
        fields = ['id', 'termsheet', 'text', 'created_at', 'updated_at']
