from django.db import models

from choices import TIME_LOG_TYPE_CHOICES
from constants import TYPE_PLENARY
from litigation.models import Dispute, Actor


# Create your models here.
class TimeLog(models.Model):
    note = models.TextField(null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    type = models.CharField(max_length=1, choices=TIME_LOG_TYPE_CHOICES, default=TYPE_PLENARY)
    stopped = models.BooleanField(default=False)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='time_logs')
    creator = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='time_logs')
    participant = models.ForeignKey(Actor, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        permissions = [
            ('view_countdown_timer_duration', 'Can view countdown timer duration')
        ]


class DurationPackage(models.Model):
    duration = models.PositiveIntegerField()
    lower_limit = models.DecimalField(max_digits=20, decimal_places=2)
    upper_limit = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.duration} seconds [{self.lower_limit}:{self.upper_limit}]"
