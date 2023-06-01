from datetime import datetime, date, timedelta

from rest_framework import serializers

from constants import CLIENT_TIMELOG_POLLING_INTERVAL
from timelog.models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)
    stopped = serializers.BooleanField(default=False)

    def _calculate_duration(self, start_time, end_time, stopped):
        if not stopped:
            return datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time) + \
                timedelta(seconds=CLIENT_TIMELOG_POLLING_INTERVAL)

        return datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)

    def _add_duration(self, instance):
        if instance.start_time and instance.end_time:
            instance.duration = self._calculate_duration(instance.start_time, instance.end_time, instance.stopped)
        else:
            instance.duration = None

        return instance

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        return self._add_duration(instance)

    def _round_to_nearest_minute(self, duration):
        """Round a datetime.timedelta object to the nearest minute.
        If seconds < 30, round down to the last minute
        If seconds >= 30, round up to the next minute
        """
        seconds_per_minute = 60
        seconds = duration.seconds
        offset = seconds % seconds_per_minute
        if not offset:
            return duration

        if offset < 30:
            return duration - timedelta(seconds=offset)

        return duration + timedelta(seconds=(60 - offset))

    def _get_hours_and_minutes_from_duration_string(self, duration_string):
        return duration_string.rsplit(':', 1)[0]

    def _process_time_duration(self, instance, duration):
        instance.duration = self._round_to_nearest_minute(duration)
        representation = super().to_representation(instance)
        representation['duration'] = self._get_hours_and_minutes_from_duration_string(representation['duration'])
        return representation

    def to_representation(self, instance):
        duration = getattr(instance, 'duration', None)

        if not duration:
            return super().to_representation(instance)

        return self._process_time_duration(instance, duration)

    class Meta:
        model = TimeLog
        fields = ['id', 'note', 'date', 'start_time', 'end_time', 'duration', 'type', 'dispute', 'creator',
                  'participant', 'stopped']
