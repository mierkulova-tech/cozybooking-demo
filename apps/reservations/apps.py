"""Django application configuration for the reservations app."""

from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    """Configuration class for the reservations application."""

    default_auto_field = "django.db.models.BigAutoField"

    name = "apps.reservations"
