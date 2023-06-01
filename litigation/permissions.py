from rest_framework.permissions import BasePermission

import constants


class IsSuperAdminOrRetrieve(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'delete', 'partial_update'] and not request.user.is_superuser:
            return False
        return True


class IsCreator(BasePermission):
    def has_permission(self, request, view):
        if request.user.actor.type != constants.CREATOR:
            return False
        return True
