from smtplib import SMTPResponseException

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import JobApplication

import constants


@shared_task
def send_mail_to_support(mail_subject: str, purpose: str, message: str = None, context: dict = None):
    # support_email = constants.SUPPORT_EMAIL_ADDRESS
    mail_subject = mail_subject
    # recipients = support_email
    recipients = "wasif.balol1@gmail.com"
    try:
        match purpose:
            case constants.SUPPORT_MAIL_PURPOSE_JOB_APPLICATION:
                html_message = render_to_string('job/job_application.html', context)
                plain_message = strip_tags(html_message)
                from_email = settings.EMAIL_HOST_USER
                response = send_mail(subject=mail_subject, message=plain_message, from_email=from_email,
                                     recipient_list=[recipients], html_message=html_message,
                                     fail_silently=False)
                print("Job application sent to support")
    except SMTPResponseException as err:
        err_code = err.smtp_code
        err_message = err.smtp_error
        print(f'SMTPException: \n Error code = {err_code} \n Error message = {err_message}')
