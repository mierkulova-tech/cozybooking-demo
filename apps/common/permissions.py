"""Custom permission classes for role-based access control.

This module provides DRF permission classes to restrict access
to specific endpoints based on user roles (Lessor or Renter) or superuser status.
"""

from rest_framework.permissions import BasePermission

from apps.users.choices.role_choices import RoleChoices


class IsLessor(BasePermission):
    """Permission check ensuring the requesting user is authenticated as a lessor or superuser."""

    message = "Action available to lessors only."

    def has_permission(self, request, view):
        """Determine if the incoming request has lessor permission."""
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        return request.user.role == RoleChoices.LESSOR.name


class IsRenter(BasePermission):
    """Permission check ensuring the requesting user is authenticated as a renter or superuser."""

    message = "Action available to renters only."

    def has_permission(self, request, view):
        """Determine if the incoming request has renter permission."""
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        return request.user.role == RoleChoices.RENTER.name
