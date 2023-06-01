from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

import constants
from .models import JobDetail, Opening, JobApplication, Experience
from .serializers import JobDetailSerializer, GetOpeningSerializer, CreateOpeningSerializer, JobApplicationSerializer, \
    ExperienceSerializer
from .tasks import send_mail_to_support


class JobDetailViewset(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = JobDetail.objects.all()
    serializer_class = JobDetailSerializer
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('type',)


class OpeningViewset(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Opening.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('position', 'employment_type',)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetOpeningSerializer
        return CreateOpeningSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class JobApplicationViewset(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('opening',)

    @staticmethod
    def create_job_application_context_dictionary(instance: JobApplication):
        experiences = instance.experience.all()
        return {'first_name': instance.first_name, "last_name": instance.last_name, "email": instance.email,
                "phone": instance.telephone, "cover_letter": instance.cover_letter,
                'experiences': ExperienceSerializer(experiences, many=True).data if experiences.exists() else None}

    @action(methods=['post'], detail=False, url_name='submit-job-application',
            url_path=r'submit-job-application', permission_classes=[AllowAny])
    def submit_job_application(self, request):
        application_id = request.data.get('application_id')
        if application_id:
            try:
                job_application = JobApplication.objects.get(id=application_id)
            except ObjectDoesNotExist:
                raise ValidationError({'application_id': ['application with this id does not exist']})
            context = JobApplicationViewset.create_job_application_context_dictionary(job_application)
            task_id = send_mail_to_support.delay(mail_subject=constants.JOB_APPLICATION_MAIL_SUBJECT,
                                                 purpose=constants.SUPPORT_MAIL_PURPOSE_JOB_APPLICATION,
                                                 context=context)
            return Response(data={"message": "Job application submitted for review successfully", 'task_id': task_id.id})
        else:
            raise ValidationError({'application_id': ['application_id is required']})


class ExperienceViewset(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('application',)
