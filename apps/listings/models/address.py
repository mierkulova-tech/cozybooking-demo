from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class Address(BaseModel):
    land = models.CharField(max_length=100, help_text="Федеральная земля (Bundesland)")

    city = models.CharField(max_length=100)

    street = models.CharField(max_length=255, blank=True)

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(regex=r"^\d{4,10}$", message="Некорректный почтовый индекс.")
        ],
    )

    class Meta:
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
        if self.city:
            self.city = self.city.strip()

        if self.land:
            self.land = self.land.strip()

        if not self.city:
            raise ValidationError({"city": "Город обязателен."})

        if not self.land:
            raise ValidationError({"land": "Федеральная земля обязательна."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.postal_code} {self.city}, {self.land}".strip()
