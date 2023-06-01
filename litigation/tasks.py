import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from celery import shared_task
from smtplib import SMTPResponseException

import constants
from core.models import User
from .models import Dispute
from django.utils.safestring import mark_safe
from docusign.views import Docusign


@shared_task
def notify_actor(context: dict):
    try:
        recipient_email = context.pop('recipient_email')
        actor_type = context.pop('actor_type')
        context.update({'text': mark_safe(context['text'])})
        html_message = render_to_string('emails/actor_invitation.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        response = send_mail(subject=context['subject'], message=plain_message, from_email=from_email,
                             recipient_list=recipient_email, html_message=html_message, fail_silently=False)
        if response == 1:
            dispute_object = Dispute.objects.get(code=context['dispute_code'])
            if actor_type == constants.CLAIMER and dispute_object.claimer_invitation_status != constants.INVITATION_STATUS_SIGNED:
                dispute_object.claimer_invitation_status = constants.INVITATION_STATUS_SENT
                dispute_object.save()
            elif actor_type == constants.RESPONDENT and dispute_object.respondent_invitation_status != constants.INVITATION_STATUS_SIGNED:
                dispute_object.respondent_invitation_status = constants.INVITATION_STATUS_SENT
                dispute_object.save()
    except SMTPResponseException as err:
        err_code = err.smtp_code
        err_message = err.smtp_error
        print(f'SMTPException: \n Error code = {err_code} \n Error message = {err_message}')


@shared_task
def send_mail_to_superuser(mail_subject, message):
    try:
        superadmins = get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True)
        mail_subject = mail_subject
        message = message
        recipients = superadmins
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=list(recipients),
            fail_silently=False,
        )
    except SMTPResponseException as err:
        err_code = err.smtp_code
        err_message = err.smtp_error
        print(f'SMTPException: \n Error code = {err_code} \n Error message = {err_message}')


@shared_task
def send_contract(dispute, subject, message, file_location):
    try:
        docusign = Docusign()
        file_path = os.path.join(settings.MEDIA_ROOT, 'library-files', file_location)
        from_email = settings.EMAIL_HOST_USER
        super_admins = User.objects.filter(is_superuser=True).values_list('email', flat=True)
        email = EmailMessage(
            subject,
            message,
            from_email, list(super_admins))
        email.attach_file(file_path)
        email.send()
        docusign.create_envelope(file_path, dispute, subject, message)
    except SMTPResponseException as err:
        err_code = err.smtp_code
        err_message = err.smtp_error
        print(f'SMTPException: \n Error code = {err_code} \n Error message = {err_message}')


@shared_task
def on_offer_status_changed(recipients: [], mail_subject, message):
    try:
        mail_subject = mail_subject
        message = message
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients,
            fail_silently=False,
        )
    except SMTPResponseException as err:
        err_code = err.smtp_code
        err_message = err.smtp_error
        print(f'SMTPException: \n Error code = {err_code} \n Error message = {err_message}')
