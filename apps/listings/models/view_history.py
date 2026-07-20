"""View history model tracking apartment page views."""

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class ViewHistory(BaseModel):
    """A record of a user (or anonymous visitor) viewing an apartment."""

    apartment = models.ForeignKey(
        "listings.Apartment",
        on_delete=models.CASCADE,
        related_name="views",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="viewed_apartments",
        null=True,
        blank=True,
    )

    class Meta:
        """Database table and indexes for ViewHistory."""

        db_table = "view_history"
        indexes = [
            models.Index(fields=["apartment"]),
        ]

    def __str__(self):
        """Return a short label showing the viewed apartment and viewer."""
        return f"view: apartment={self.apartment_id} by user={self.user_id}"
