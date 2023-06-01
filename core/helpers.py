from typing import Optional

from django.conf import settings
from django.contrib.auth.models import Group


class Helpers:
    @staticmethod
    def add_user_to_actor_group(user: settings.AUTH_USER_MODEL, group: Optional[str] = 'admin') -> None:
        """
        This function adds user to the desired actor group whose name is passed as a parameter to the function.
        If no group name is specified the user is by default added to the admin group.
        """
        actor_group = Group.objects.filter(name=group.title()).first()
        user.groups.add(actor_group)
