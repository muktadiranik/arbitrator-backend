import os

from django.core.validators import FileExtensionValidator
from django.db import models
import choices
from core.models import User
from django.contrib.contenttypes.fields import GenericRelation
from choices import *
from uuid import uuid4
from notes.models import Note


class Actor(models.Model):
    display_picture = models.ImageField(upload_to='display-pictures/', null=True, blank=True)
    user = models.OneToOneField(User, related_name='actor', on_delete=models.CASCADE)
    account = models.CharField(choices=ACCOUNT_CHOICES, max_length=16, null=True, blank=True)
    type = models.SlugField(choices=TYPE_CHOICES, max_length=25, null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=32, null=True, blank=True)
    company = models.CharField(max_length=32, null=True, blank=True)
    phone_number = models.CharField(verbose_name='Phone Number', max_length=16, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    signed_up_at = models.DateTimeField(auto_now_add=True, editable=True)
    relation = models.CharField(max_length=32, null=True, blank=True)
    creator = models.ForeignKey('Actor', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user}'


class Timezone(models.Model):
    actor = models.OneToOneField(Actor, related_name='timezone', on_delete=models.CASCADE)
    offset = models.CharField(max_length=32)
    description = models.CharField(max_length=128)


class Address(models.Model):
    user = models.ForeignKey(Actor, related_name='address', on_delete=models.CASCADE)
    first_address = models.CharField(max_length=128, null=True, blank=True)
    second_address = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)
    state = models.CharField(max_length=32, null=True, blank=True)
    zip = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return f'{self.user}'


# CLAIMER MODEL AND MANAGER
class GeneralManager(models.Manager):
    def __init__(self, type=None):
        super(GeneralManager, self).__init__()
        self.type = type

    def get_queryset(self):
        return super(GeneralManager, self).get_queryset().filter(type=self.type)


class Claimer(Actor):
    TYPE = constants.CLAIMER
    objects = GeneralManager(type=TYPE)

    class Meta:
        proxy = True


class Arbitrator(Actor):
    TYPE = constants.ARBITRATOR
    objects = GeneralManager(TYPE)

    class Meta:
        proxy = True


class Creator(Actor):
    TYPE = constants.CREATOR
    objects = GeneralManager(TYPE)

    class Meta:
        proxy = True


class Witness(Actor):
    TYPE = constants.WITNESS
    objects = GeneralManager(TYPE)

    class Meta:
        proxy = True


class Respondent(Actor):
    TYPE = constants.RESPONDENT
    objects = GeneralManager(TYPE)

    class Meta:
        proxy = True


class Dispute(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=24)
    creator = models.ForeignKey(Creator, related_name='disputes', on_delete=models.CASCADE)
    arbitrator = models.ForeignKey(Arbitrator, related_name='disputes_assigned', on_delete=models.PROTECT, null=True,
                                   blank=True)
    claimer = models.ForeignKey(Claimer, related_name='disputes_claimed', on_delete=models.PROTECT, null=True,
                                blank=True)
    respondent = models.ForeignKey(Respondent, related_name='disputes_responded', on_delete=models.PROTECT, null=True,
                                   blank=True)
    witness = models.ManyToManyField(Witness, related_name='disputes_witnessed', blank=True)
    code = models.CharField(max_length=24, unique=True)
    type = models.CharField(choices=DISPUTE_TYPE_CHOICES, max_length=24)
    respondent_invitation_status = models.CharField(choices=INVITATION_STATUS_CHOICES, default='pending', max_length=16)
    claimer_invitation_status = models.CharField(choices=INVITATION_STATUS_CHOICES, default='pending', max_length=16)
    contains_witness = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'{self.code}'

    class Meta:
        permissions = [
            ("view_disputes_table", "Can view disputes table")
        ]


class Claim(models.Model):
    dispute = models.OneToOneField(Dispute, related_name='claim', on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = GenericRelation(Note)
    claimed_amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f'Claim against dispute ({self.dispute.code})'


class UUID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    actor = models.OneToOneField(Actor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    max_age = models.PositiveIntegerField(default=172800)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.actor}'


class Evidence(models.Model):
    claim = models.ForeignKey(Claim, related_name='evidence', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='evidences/',
                                  validators=[FileExtensionValidator(
                                      allowed_extensions=["pdf", "doc", "docx", "jpg", "png", "mp4", ".xls", ".xlsx"])])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(Actor, on_delete=models.CASCADE)

    @property
    def extension(self):
        name, extension = os.path.splitext(self.attachment.name)
        return extension.lower()

    @property
    def size(self):
        return self.attachment.size


class Offer(models.Model):
    creator = models.ForeignKey(Actor, related_name="offer", on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, related_name="offer", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offered_amount = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.CharField(default='usd', max_length=10)
    status = models.CharField(max_length=16, choices=OFFER_CHOICES)
    offer_accepted_modal_rendered = models.BooleanField(default=False)
    offer_received_modal_rendered = models.BooleanField(default=False)

    def __str__(self):
        return f'offer against dispute ({self.claim.dispute.code})'


class Timeline(models.Model):
    dispute = models.ForeignKey(Dispute, related_name='timeline', on_delete=models.CASCADE)
    name = models.CharField(max_length=48)
    deadline_date = models.DateField()
    completed = models.BooleanField(default=False)
    end_date = models.DateField(default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.name} : {self.dispute.code}'


class ActionNames(models.Model):
    name = models.CharField(choices=choices.DISPUTE_USER_ACTIONS, max_length=24)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Action Names"

    def __str__(self):
        return f'{self.name.upper()}'


class Actions(models.Model):
    action = models.ForeignKey(ActionNames, related_name='action_values', on_delete=models.CASCADE)
    value = models.CharField(choices=choices.DISPUTE_USER_ACTIONS_VALUES, max_length=24)

    class Meta:
        verbose_name_plural = "Actions"

    def __str__(self):
        return f'{self.action.name}: {self.value}'


class DisputeActorActions(models.Model):
    dispute = models.ForeignKey(Dispute, related_name='actions', on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, related_name='actions', on_delete=models.CASCADE)
    action = models.ManyToManyField(Actions)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Dispute Actor Actions"

    def __str__(self):
        return f'User {self.actor.user.email} on {self.dispute.code} performed ' \
               f'{self.action.values("action__name", "value")}'


class EmailTemplate(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='email_template')
    template_title = models.CharField(max_length=24)
    email_subject = models.CharField(max_length=48)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='email_template')
    content = models.CharField(max_length=1000)

    @property
    def dispute_type(self):
        return self.dispute.type

    @property
    def creator_name(self):
        return f'{self.dispute.creator.user.first_name} {self.dispute.creator.user.last_name}'

    @property
    def recipient_name(self):
        return f'{self.actor.user.first_name} {self.actor.user.last_name}'

    @property
    def recipient_email(self):
        return f'{self.actor.user.email}'


class SettlementAgreements(models.Model):
    dispute = models.OneToOneField(Dispute, on_delete=models.CASCADE)
    content = models.TextField(max_length=50000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
