"""Django administration panel configuration for the users app.

This module registers the User model with the Django admin interface
and configures list displays, filters, and search fields for administrative management.
"""

from django.contrib import admin

from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration interface for the User model."""

    list_display = ["id", "email", "name", "role", "is_active", "is_staff"]

    list_filter = ["role", "is_active", "is_staff"]

    search_fields = ["email", "name"]
