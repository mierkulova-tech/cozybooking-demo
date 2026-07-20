"""Django application configuration for the reviews app."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Configuration class for the reviews application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"
