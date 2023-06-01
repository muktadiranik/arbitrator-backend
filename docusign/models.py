from django.db import models
from litigation.models import Dispute


# Create your models here.
class DocuSignEnvelope(models.Model):
    dispute = models.ForeignKey(Dispute, related_name='envelope', on_delete=models.CASCADE)
    envelope_id = models.CharField(max_length=96)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
