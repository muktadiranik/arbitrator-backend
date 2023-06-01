from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import JobDetail, Opening, JobApplication, Experience


class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetail
        fields = ['id', 'text', 'type', 'created_at', 'updated_at']


class GetOpeningSerializer(serializers.ModelSerializer):
    details = JobDetailSerializer(many=True)

    class Meta:
        model = Opening
        fields = ['id', 'title', 'description', 'position', 'employment_type', 'linked_in_url', 'details', 'created_at',
                  'updated_at']


class CreateOpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opening
        fields = ['id', 'title', 'description', 'position', 'employment_type', 'linked_in_url', 'details', 'created_at',
                  'updated_at']


class JobApplicationSerializer(serializers.ModelSerializer):
    experience = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'opening', 'first_name', 'last_name', 'email', 'telephone', 'cover_letter', 'experience',
                  'created_at', 'updated_at']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'application', 'job_title', 'company', 'start_date', 'end_date', 'currently_working',
                  'description', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method != 'PATCH':
            end_date = attrs.get('end_date')
            currently_working = attrs.get('currently_working')
            if not currently_working and not end_date:
                raise ValidationError(message={"End date": ["End date is necessary"]})
        return super().validate(attrs)
