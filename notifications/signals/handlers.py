from actstream.models import Action
from django.db.models.signals import post_save
from django.dispatch import receiver

import constants
from notifications.consumer import send_notification_message


@receiver(post_save, sender=Action)
def activity_stream_handler(sender, instance, created, **kwargs):
    verb = instance.verb
    if created and verb == constants.PENDING and instance.actor.actor.type != constants.RESPONDENT:
        dispute = instance.target
        sender = instance.actor
        user_id = instance.actor_object_id
        sent = send_notification_message(user_id, f"{dispute.respondent.user.get_full_name()} has created the offer on {dispute}",
                                         'offer_notification_group')
        if sent:
            instance.data["sent"] = True
            Action.objects.filter(id=instance.id).update(data=instance.data)

    elif created and \
            (verb == constants.REJECTED or
             verb == constants.ACCEPTED or
             verb == constants.COUNTER_OFFER) \
            and instance.actor.actor.type != constants.CLAIMER:
        dispute = instance.target
        sender = instance.actor
        user_id = instance.actor_object_id
        sent = send_notification_message(user_id, f"{sender} has {verb} the offer on {dispute}",
                                         'offer_notification_group')
        if sent:
            instance.data["sent"] = True
            Action.objects.filter(id=instance.id).update(data=instance.data)
