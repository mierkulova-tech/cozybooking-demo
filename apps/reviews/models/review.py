"""Review model representing a rating and comment left after a completed stay."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class Review(BaseModel):
    """A review left by a renter for a completed reservation."""

    listing = models.ForeignKey(
        "listings.Apartment",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reservation = models.OneToOneField(
        "reservations.Reservation",
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)

    class Meta:
        """Database table, ordering, and constraints for Review."""

        db_table = "reviews"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_range",
            ),
        ]

    def clean(self):
        """Validate that the review is consistent with its linked reservation.

        Raises:
            ValidationError: If the reservation link is missing, the rating
                is out of range, or the user/listing don't match the
                reservation's user/listing.
        """
        if not self.reservation_id:
            raise ValidationError({"reservation": "A review must be linked to a reservation."})

        if self.rating is not None:
            if self.rating < 1 or self.rating > 5:
                raise ValidationError({"rating": "Rating must be between 1 and 5."})

        if self.reservation_id:
            if self.user_id and self.reservation.user_id != self.user_id:
                raise ValidationError(
                    {
                        "user": "The review must be left by the same user "
                        "specified on the reservation."
                    }
                )

        if self.listing_id and self.reservation.listing_id != self.listing_id:
            raise ValidationError(
                {"listing": "The reviewed listing must match the reservation's listing."}
            )

    def save(self, *args, **kwargs):
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a short label showing the review id, listing, and rating."""
        return f"Review #{self.id} listing={self.listing_id} rating={self.rating}"
