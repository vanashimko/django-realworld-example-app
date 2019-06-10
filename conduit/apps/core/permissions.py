from rest_framework import permissions
from rest_framework.compat import is_authenticated

from apps.core.models import OwnedModel


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request in ('GET', 'HEAD', 'OPTIONS'):
            return True
        if not request.user:
            return False
        if not is_authenticated(request.user):
            return False
        if isinstance(obj, OwnedModel):
            return obj.owner == request.user.profile
        else:
            return True
