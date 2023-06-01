from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from litigation.models import Dispute, DisputeActorActions, Actions, Arbitrator
from django.db.models.signals import post_save, m2m_changed, pre_delete
from django.dispatch import receiver
import constants
from core.models import User
from termsheet.serializers import TermsheetSerializer
from termsheet.models import TermSheet, TermsheetSection
import datetime
from django.db.models import Count
from ..tasks import send_mail_to_superuser


def create_term_sheet_sections(term_sheet: TermSheet):
    term_sheet_sections = []
    for section_title in constants.TERM_SHEET_SECTION_TITLES:
        term_sheet_section = TermsheetSection(termsheet=term_sheet, title=section_title)
        term_sheet_sections.append(term_sheet_section)
    TermsheetSection.objects.bulk_create(term_sheet_sections)


def create_termsheet(dispute_id: int):
    term_sheet = {"dispute": dispute_id, 'title': constants.TERM_SHEET_TITLE}
    serialized_term_sheet = TermsheetSerializer(data=term_sheet)
    serialized_term_sheet.is_valid(raise_exception=True)
    created_term_sheet = serialized_term_sheet.save()
    create_term_sheet_sections(created_term_sheet)


def update_dispute_status(dispute: Dispute, status: str):
    Dispute.objects.filter(id=dispute.id).update(status=status)


def update_dispute_timeline(dispute: Dispute):
    dispute.timeline.filter(name='Waiting for the other side').update(end_date=datetime.date.today(), completed=True)


@receiver(post_save, sender=Dispute)
def create_term_sheet(sender, **kwargs):
    dispute = kwargs.get('instance')
    term_sheet = TermSheet.objects.filter(dispute_id=dispute.id)
    if dispute and dispute.arbitrator and not term_sheet.exists():
        create_termsheet(dispute.id)


@receiver(post_save, sender=Dispute)
def dispute_status_update(sender, **kwargs):
    dispute = kwargs.get('instance')
    try:
        accepted_offers = dispute.claim.offer.filter(status=constants.ACCEPTED)
    except ObjectDoesNotExist:
        accepted_offers = None

    if dispute and dispute.respondent_invitation_status == constants.INVITATION_STATUS_SIGNED and \
            dispute.claimer_invitation_status == constants.INVITATION_STATUS_SIGNED and \
            dispute.status != constants.IN_PROGRESS and not accepted_offers:
        try:
            with transaction.atomic():
                update_dispute_status(dispute, constants.IN_PROGRESS)
                update_dispute_timeline(dispute)
        except IntegrityError as error:
            print(error)


@receiver(m2m_changed, sender=DisputeActorActions.action.through)
def on_rejection_limit_reached(sender, **kwargs):
    action = kwargs.get('action')
    instance = kwargs.get('instance')
    if action == 'post_add':
        actions = kwargs.get('pk_set')
        if not actions:
            return
        reject_values = instance.action.filter(pk__in=actions, value=constants.DISPUTE_USER_ACTION_REJECTED).exists()
        if not reject_values:
            return
        disputes_rejections = DisputeActorActions.objects.filter(action__action__name=constants.APPROVAL_ACTION,
                                                                 action__value=constants.DISPUTE_USER_ACTION_REJECTED).values(
            'actor__user_id', 'actor__user__first_name', 'actor__user__last_name', 'actor__user__email').annotate(
            rejections=Count('actor__user__id')).order_by()
        arbitrators = [
            {
                "First Name": rejection['actor__user__first_name'],
                "Last Name": rejection['actor__user__last_name'],
                "Email": rejection['actor__user__email'],
                "Rejections": rejection['rejections']
            }
            for rejection in disputes_rejections if rejection['rejections'] >= constants.DISPUTE_REJECTION_THRESHOLD]
        if arbitrators:
            task_id = send_mail_to_superuser.delay(mail_subject="Rejection limit reached",
                                                   message=f"{arbitrators} \nThe mentioned arbitrators have reached the dispute rejection threshold.")
            print(f'Dispute Rejection mail task Id: {task_id}')


@receiver(m2m_changed, sender=Dispute.witness.through)
def on_witness_added(sender, instance, **kwargs):
    action = kwargs.get('action')
    witnesses = instance.witness.through.objects.filter(dispute_id=instance.id)

    if action == 'post_add':
        if witnesses.exists():
            instance.contains_witness = True
            instance.save()


@receiver(pre_delete, sender=User)
def on_witness_deleted(sender, instance, **kwargs):
    disputes = Dispute.objects.filter(witness__id=instance.actor.id)
    for dispute in disputes:
        witnesses = dispute.witness.through.objects \
            .filter(dispute_id=dispute.id) \
            .exclude(witness_id=instance.actor.id)
        if not witnesses.exists():
            dispute.contains_witness = False
            dispute.save()


def fetch_unavailable_arbitrators(arbitrator_ids_to_exclude: list = None):
    if arbitrator_ids_to_exclude:
        arbitrators = Dispute.objects.filter(arbitrator__isnull=False).values_list(
            'arbitrator_id', flat=True).annotate(
            assigned_disputes=Count('arbitrator_id')).filter(
            assigned_disputes__gte=constants.DISPUTE_REJECTION_THRESHOLD).order_by()
        arbitrators = list(arbitrators) + arbitrator_ids_to_exclude
    else:
        arbitrators = Dispute.objects.filter(arbitrator__isnull=False).values_list(
            'arbitrator_id', flat=True).annotate(
            assigned_disputes=Count('arbitrator_id')).filter(
            assigned_disputes__gte=constants.DISPUTE_REJECTION_THRESHOLD).order_by()

    if arbitrators:
        return list(arbitrators)
    return []


@receiver(m2m_changed, sender=DisputeActorActions.action.through)
def assigned_dispute(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        # Get the latest action
        latest_action = instance.action.order_by('-id').first()

        # Fetch Approval action
        dispute_approve_action = Actions.objects.get(action__name=constants.APPROVAL_ACTION,
                                                     value=constants.DISPUTE_USER_ACTION_PENDING)

        if latest_action.action.name == constants.STRAIGHT_TO_HEARING_ACTION and \
                latest_action.value == constants.DISPUTE_USER_ACTION_ACCEPTED or \
                latest_action.action.name == constants.APPROVAL_ACTION and \
                latest_action.value == constants.DISPUTE_USER_ACTION_REJECTED:
            # Checking if the action in "Approval" and value is "reject" then fetching the arbitrators already rejected the current dispute
            if latest_action.action.name == constants.APPROVAL_ACTION and latest_action.value == constants.DISPUTE_USER_ACTION_REJECTED:
                arbitrators_already_rejected = list(DisputeActorActions.objects.filter(dispute_id=instance.dispute_id,
                                                                                       action__action__name=constants.APPROVAL_ACTION,
                                                                                       action__value=constants.DISPUTE_USER_ACTION_REJECTED).values_list(
                    'actor_id', flat=True))
                # Appending the current actor id so the dispute won't be assigned to these arbitrator again
                arbitrators_already_rejected.append(instance.actor.id)
                arbitrators = fetch_unavailable_arbitrators(arbitrator_ids_to_exclude=arbitrators_already_rejected)

            else:
                arbitrators = fetch_unavailable_arbitrators()
            all_arbitrators = Arbitrator.objects.all().values_list('id', flat=True).exclude(id__in=arbitrators)
            for arbitrator in all_arbitrators:
                dispute_action = DisputeActorActions.objects.create(dispute_id=instance.dispute_id,
                                                                    actor_id=arbitrator)
                dispute_action.action.add(
                    dispute_approve_action)
                break
