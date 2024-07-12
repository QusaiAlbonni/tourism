from rest_framework import permissions

class isAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_admin or request.user.is_staff))
class isAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_admin or request.user.is_staff))
class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user.is_staff or user.is_admin) or obj.pk == user.pk
class CanManageActivitiesOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.has_perm('app_auth.manage_activities'))
class CanManageActivities(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('app_auth.manage_activities'))
class CanManagePropertiesOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.has_perm('app_auth.manage_properties'))
class CanManageCarRentalOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.has_perm('app_auth.manage_car_rental'))
class isClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_admin and not request.user.is_staff)
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    

class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False