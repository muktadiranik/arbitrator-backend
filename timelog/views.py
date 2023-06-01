from datetime import timedelta

from django.db.models import ExpressionWrapper, When, Case, F, Sum, Max, Min
from django.db.models.fields import DurationField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from constants import CLIENT_TIMELOG_POLLING_INTERVAL
from litigation.models import Dispute
from timelog.models import TimeLog, DurationPackage
from timelog.serializers import TimeLogSerializer


# Create your views here.
class TimeLogViewSet(ModelViewSet):
    serializer_class = TimeLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'dispute', 'participant']

    def get_queryset(self):
        return TimeLog.objects.all() \
            .annotate(duration=Case(
            When(stopped=False,
                 then=ExpressionWrapper(
                     F('end_time') - F('start_time') + timedelta(seconds=CLIENT_TIMELOG_POLLING_INTERVAL),
                     output_field=DurationField()
                 )),
            default=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            ),
        )
        ) \
            .order_by('-date')

    def _calculate_duration(self):
        return Case(
            When(stopped=False,
                 then=ExpressionWrapper(
                     F('end_time') - F('start_time') + timedelta(seconds=CLIENT_TIMELOG_POLLING_INTERVAL),
                     output_field=DurationField()
                 )),
            default=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            )
        )

    def _get_total_duration(self, queryset):
        total_duration = queryset \
            .annotate(
            duration=self._calculate_duration()
        ) \
            .aggregate(
            total_duration=Sum('duration')
        ) \
            .get('total_duration')

        if total_duration:
            return total_duration.seconds

        return 0

    def _get_claimed_amount(self, dispute_id):
        dispute = Dispute.objects.get(pk=dispute_id)
        return dispute.claim.claimed_amount

    def _get_allowed_duration(self, claimed_amount):
        package = DurationPackage.objects.filter(lower_limit__lte=claimed_amount,
                                                 upper_limit__gte=claimed_amount) \
            .first()

        if package:
            return package.duration

        min_lower_limit = DurationPackage.objects.aggregate(least_lower_limit=Min('lower_limit'))['least_lower_limit']
        max_upper_limit = DurationPackage.objects.aggregate(highest_upper_limit=Max('upper_limit'))[
            'highest_upper_limit']

        if claimed_amount < min_lower_limit:
            return DurationPackage.objects.filter(lower_limit=min_lower_limit).first().duration

        if claimed_amount > max_upper_limit:
            return DurationPackage.objects.filter(upper_limit=max_upper_limit).first().duration

    @action(detail=False, url_name='get_remaining_duration', url_path='remaining-duration')
    def get_remaining_duration(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        total_duration_in_seconds = self._get_total_duration(queryset)

        claimed_amount = self._get_claimed_amount(request.query_params.get('dispute'))

        allowed_duration_in_seconds = self._get_allowed_duration(claimed_amount)

        remaining_duration_in_seconds = allowed_duration_in_seconds - total_duration_in_seconds

        if remaining_duration_in_seconds < 0:
            remaining_duration_in_seconds = 0

        return Response({'remaining_duration': remaining_duration_in_seconds}, status=status.HTTP_200_OK)
