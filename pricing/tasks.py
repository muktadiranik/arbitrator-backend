from smtplib import SMTPResponseException

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_payment_details_to_creator(mail_subject, message, recipients):
    try:
        mail_subject = mail_subject
        message = message
        recipients = recipients
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
