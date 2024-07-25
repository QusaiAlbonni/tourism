from rest_framework import permissions

class CanManageEventOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.has_perm('events.manage_event'))
