"""Django application configuration for the common app."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration class for the common application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
