from django.db import models
from pricing.models import TimestampedModel
from choices import JOB_TYPE_CHOICES, EMPLOYMENT_TYPE_CHOICES, JOB_DETAILS_TYPE_CHOICES


# Create your models here.

class JobDetail(TimestampedModel):
    text = models.CharField(max_length=192)
    type = models.CharField(choices=JOB_DETAILS_TYPE_CHOICES, max_length=12)

    def __str__(self):
        return f"{self.type}: {self.text}"


class Opening(TimestampedModel):
    title = models.CharField(max_length=48)
    description = models.TextField()
    position = models.CharField(choices=JOB_TYPE_CHOICES, max_length=24)
    employment_type = models.CharField(choices=EMPLOYMENT_TYPE_CHOICES, max_length=36)
    linked_in_url = models.URLField(null=True, blank=True)
    details = models.ManyToManyField(JobDetail, related_name='openings')

    def __str__(self):
        return f"{self.title} ({self.position})"


class JobApplication(TimestampedModel):
    opening = models.ForeignKey(Opening, related_name='job_applications', on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    cover_letter = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.opening.title}"


class Experience(TimestampedModel):
    application = models.ForeignKey(JobApplication, related_name='experience', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company}"
