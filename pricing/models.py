from django.db import models

import choices
from choices import CURRENCY_CHOICES
from litigation.models import Actor, Creator


# Create your models here.

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Feature(TimestampedModel):
    text = models.TextField()

    def __str__(self):
        return f'{self.text} '


class Plan(TimestampedModel):
    name = models.CharField(max_length=16)
    disputes = models.IntegerField()
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    active = models.BooleanField()
    feature = models.ManyToManyField(Feature, related_name='features')
    stripe_product_id = models.CharField(default="None", max_length=48)
    description = models.CharField(max_length=192)

    def __str__(self):
        return self.name


class PaymentDetail(TimestampedModel):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='payment_details')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='payments')
    stripe_payment_status = models.CharField(choices=choices.PAYMENT_STATUS_CHOICES, default="None", max_length=24)
    stripe_payment_id = models.CharField(max_length=48, default="None")
    is_subscription_active = models.BooleanField(default=False)


class CreatorDisputeCount(TimestampedModel):
    creator = models.OneToOneField(Creator, on_delete=models.CASCADE, related_name='disputes_count')
    disputes_created = models.IntegerField()
    disputes_available = models.IntegerField()
