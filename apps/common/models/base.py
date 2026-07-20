"""Base abstract model providing common timestamp fields."""

from django.db import models


class BaseModel(models.Model):
    """Abstract base model that adds creation and update timestamps.

    All project models should inherit from this class to get consistent
    `created_at` / `updated_at` tracking without duplicating fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Marks this model as abstract (no database table of its own)."""

        abstract = True
