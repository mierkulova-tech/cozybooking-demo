"""Address model representing the location of a listed apartment."""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class Address(BaseModel):
    """A physical address (federal state, city, street, postal code)."""

    land = models.CharField(max_length=100, help_text="Federal state (Bundesland)")

    city = models.CharField(max_length=100)

    street = models.CharField(max_length=255, blank=True)

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[RegexValidator(regex=r"^\d{4,10}$", message="Invalid postal code.")],
    )

    class Meta:
        """Database table, indexes, and constraints for Address."""

        db_table = "addresses"

        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["land"]),
        ]

        constraints = [
            models.CheckConstraint(
                condition=~Q(city=""),
                name="address_city_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(land=""),
                name="address_land_not_empty",
            ),
        ]

    def clean(self):
        """Strip whitespace from city/land and require both to be present."""
        if self.city:
            self.city = self.city.strip()

        if self.land:
            self.land = self.land.strip()

        if not self.city:
            raise ValidationError({"city": "City is required."})

        if not self.land:
            raise ValidationError({"land": "Federal state is required."})

    def save(self, *args, **kwargs):
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the postal code, city, and federal state as a single line."""
        return f"{self.postal_code} {self.city}, {self.land}".strip()
