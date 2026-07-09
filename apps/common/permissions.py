from rest_framework.permissions import BasePermission

from apps.users.choices.role_choices import RoleChoices


class IsLessor(BasePermission):
    message = "Действие доступно только арендодателю."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        return request.user.role == RoleChoices.LESSOR.name


class IsRenter(BasePermission):
    message = "Действие доступно только арендатору."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        return request.user.role == RoleChoices.RENTER.name
