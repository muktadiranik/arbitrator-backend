from django.db import models
from litigation.models import Dispute


class Lane(models.Model):
    name = models.CharField(max_length=16)
    display_name = models.CharField(max_length=16)
    is_proposal = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.display_name}'

    class Meta:
        permissions = [
            ('view_noteboard', 'Can view noteboard')
        ]


class Note(models.Model):
    dispute = models.ForeignKey(Dispute, related_name='notes', on_delete=models.CASCADE)
    lane = models.ForeignKey(Lane, related_name='notes', on_delete=models.CASCADE)
    text = models.TextField()
    is_strike = models.BooleanField(default=False, null=True, blank=True)
    is_caucus = models.BooleanField(default=False, null=True, blank=True)
    is_mediator = models.BooleanField(default=False, null=True, blank=True)
    is_blur = models.BooleanField(default=False, null=True, blank=True)
    is_party_attributed = models.BooleanField(default=False, null=True, blank=True)
    parent = models.ManyToManyField('self', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    countered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}: {self.lane.name} against dispute:{self.dispute.code}'


class ProposalRelation(models.Model):
    note = models.OneToOneField(Note, related_name='relations', on_delete=models.CASCADE)
    base_proposal = models.ForeignKey(Note, related_name='base_proposal', on_delete=models.CASCADE, null=True,
                                      blank=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Related to {self.note}'
