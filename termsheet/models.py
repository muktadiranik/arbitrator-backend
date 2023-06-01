from django.db import models
from litigation.models import Dispute


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TermsheetTitle(models.Model):
    text = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return f'{self.text}'


class SectionTitle(models.Model):
    text = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return f'{self.text}'


class TermSheet(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)
    title = models.TextField(max_length=40)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        permissions = [
            ('print_termsheet', 'Can print termsheet')
        ]


class DigitalSignature(BaseModel):
    termsheet = models.ForeignKey(TermSheet, related_name='signatures', on_delete=models.CASCADE)
    text = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return f'{self.text}'


class TermsheetSection(BaseModel):
    termsheet = models.ForeignKey(TermSheet, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=40, null=False, blank=False)
    text = models.TextField()

    def __str__(self):
        return f'{self.title}'
