"""Bill Permissions."""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Custom permission to check if user is in the 'admin' group."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="admin").exists()
        )
