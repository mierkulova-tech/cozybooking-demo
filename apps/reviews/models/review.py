from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models.base import BaseModel


class Review(BaseModel):
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
        db_table = "reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review #{self.id} listing={self.listing_id} rating={self.rating}"
