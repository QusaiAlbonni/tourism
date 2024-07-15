from rest_framework import permissions

class CanScanReservations(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('reservations.scan_reservations'))