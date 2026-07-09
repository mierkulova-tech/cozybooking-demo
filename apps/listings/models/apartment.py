from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel
from apps.listings.choices.housing_choices import HousingTypeChoices


class Apartment(BaseModel):
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveSmallIntegerField()
    housing_type = models.CharField(max_length=20, choices=HousingTypeChoices.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "apartments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["rooms"]),
            models.Index(fields=["housing_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.price}€"
