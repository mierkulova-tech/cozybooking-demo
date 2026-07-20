"""Apartment listing model with pricing, capacity, and moderation fields."""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel
from apps.listings.choices.housing_choices import HousingTypeChoices


class Apartment(BaseModel):
    """A rentable apartment listing owned by a lessor."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="apartments",
    )

    address = models.ForeignKey(
        "listings.Address",
        on_delete=models.PROTECT,
        related_name="apartments",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="Price must be greater than zero.")],
    )

    rooms = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Must have at least 1 room."),
            MaxValueValidator(5, message="Too many rooms — please check the value, maximum is 5."),
        ]
    )

    housing_type = models.CharField(max_length=20, choices=HousingTypeChoices.choices)
    views_count = models.PositiveIntegerField(default=0, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Database table, indexes, and constraints for Apartment."""

        db_table = "apartments"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["rooms"]),
            models.Index(fields=["housing_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["views_count"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="apartment_price_positive",
            ),
            models.CheckConstraint(
                condition=Q(rooms__gte=1) & Q(rooms__lte=5),
                name="apartment_rooms_reasonable",
            ),
            models.CheckConstraint(
                condition=Q(title__length__gte=5),
                name="apartment_title_min_length",
            ),
            models.CheckConstraint(
                condition=Q(description__length__gte=5),
                name="apartment_description_min_length",
            ),
            models.CheckConstraint(
                condition=Q(housing_type__in=HousingTypeChoices.values),
                name="apartment_housing_type_valid",
            ),
        ]

    def clean(self):
        """Strip whitespace and enforce minimum length on title/description."""
        if self.title:
            self.title = self.title.strip()

        if self.description:
            self.description = self.description.strip()

        if len(self.title) < 5:
            raise ValidationError({"title": "Title must contain at least 5 characters."})

        if len(self.description.strip()) < 5:
            raise ValidationError({"description": "Description is too short."})

    def save(self, *args, **kwargs):
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the apartment title and price."""
        return f"{self.title} — {self.price}€"
