
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

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
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=F("start_date")),
                name="reservation_end_after_start",
            ),
            models.CheckConstraint(
                condition=Q(status__in=StatusChoices.values),
                name="reservation_status_valid",
            ),
        ]

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": "Дата окончания должна быть позже даты начала."}
            )

        if self.start_date < timezone.now().date():
            raise ValidationError(
                {"start_date": "Нельзя создать бронирование в прошлом."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation #{self.id} listing={self.listing_id} [{self.status}]"
