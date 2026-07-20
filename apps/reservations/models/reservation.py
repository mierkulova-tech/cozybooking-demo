"""Reservation model representing a booking of an apartment for a date range."""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.common.models.base import BaseModel
from apps.reservations.choices.status_choices import StatusChoices


class Reservation(BaseModel):
    """A booking made by a renter for an apartment over a date range."""

    listing = models.ForeignKey(
        "listings.Apartment",
        on_delete=models.PROTECT,
        related_name="reservations",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="Price must be greater than zero.")],
    )

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    class Meta:
        """Database table, indexes, and constraints for Reservation."""

        db_table = "reservations"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["listing", "status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["listing", "start_date", "end_date"]),
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
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="reservation_price_positive",
            ),
        ]

    def clean(self):
        """Validate date range, ownership, and booking-window business rules.

        Raises:
            ValidationError: If end_date is not after start_date, if the user
                tries to book their own listing, if start_date is moved into
                the past, or if start_date is more than a year in the future.
        """
        super().clean()

        current_date = timezone.now().date()

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError({"end_date": "End date must be later than the start date."})

        if self.user_id and self.listing_id:
            if self.listing.owner_id == self.user_id:
                raise ValidationError({"user": "You cannot book your own listing."})

        if not self.pk:
            if self.start_date and self.start_date < current_date:
                raise ValidationError({"start_date": "Cannot create a reservation in the past."})
        else:
            original = Reservation.objects.get(pk=self.pk)
            if original.start_date != self.start_date and self.start_date < current_date:
                raise ValidationError({"start_date": "Cannot move a reservation to a past date."})

        if self.start_date and (self.start_date - current_date).days > 365:
            raise ValidationError({"start_date": "Reservations can be made at most 1 year ahead."})

    def save(self, *args, **kwargs):
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a short label showing the reservation id, listing, and status."""
        return f"Reservation #{self.id} listing={self.listing_id} [{self.status}]"
