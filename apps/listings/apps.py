"""Django application configuration for the listings module.

This module defines the AppConfig subclass for listings and registers
the Length database function lookup for CharField and TextField models on startup.
"""

from django.apps import AppConfig
from django.db.models import CharField, TextField
from django.db.models.functions import Length


class ListingsConfig(AppConfig):
    """Application configuration class for the listings app."""

    name = "apps.listings"

    def ready(self):
        """Register the Length lookup for character and text fields.

        Registered when the application is ready.
        """
        CharField.register_lookup(Length)
        TextField.register_lookup(Length)
