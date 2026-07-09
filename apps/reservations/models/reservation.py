from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel
from apps.reservations.choices.status_choices import StatusChoices


class Reservation(BaseModel):
    listing = models.ForeignKey(
        "listings.Apartment",
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    class Meta:
        db_table = "reservations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["listing", "status"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Reservation #{self.id} listing={self.listing_id} [{self.status}]"
