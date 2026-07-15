from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class ViewHistory(BaseModel):
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
        db_table = "view_history"
        indexes = [
            models.Index(fields=["apartment"]),
        ]

    def __str__(self):
        return f"view: apartment={self.apartment_id} by user={self.user_id}"
