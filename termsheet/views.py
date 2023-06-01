from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *


class TermsheetViewset(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    serializer_class = TermsheetSerializer
    filterset_fields = ('dispute',)

    def get_queryset(self):
        return TermSheet.objects.filter(dispute__arbitrator__id=self.request.user.actor.id)


class TermsheetTitleViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class = TermsheetTitleSerializer
    queryset = TermsheetTitle.objects.all()


class SectionTitleViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class = SectionTitleSerializer
    queryset = SectionTitle.objects.all()


class DigitalSignatureViewset(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = DigitalSignatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('termsheet',)

    def get_queryset(self):
        return DigitalSignature.objects.filter(termsheet__dispute__arbitrator__id=self.request.user.actor.id)


class TermsheetSectionViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    serializer_class = TermsheetSectionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('termsheet',)

    def get_queryset(self):
        return TermsheetSection.objects.filter(termsheet__dispute__arbitrator__id=self.request.user.actor.id).order_by(
            'id')
