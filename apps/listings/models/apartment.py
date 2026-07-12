

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models

from django.db.models import Q, CharField, TextField

from django.db.models.functions import Length

from apps.common.models.base import BaseModel

from apps.listings.choices.housing_choices import HousingTypeChoices


CharField.register_lookup(Length)
TextField.register_lookup(Length)


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

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Цена должна быть больше нуля.")],
    )

    rooms = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Должна быть минимум 1 комната."),
            MaxValueValidator(
                5, message="Слишком много комнат — проверьте значение, максимум 5."
            ),
        ]
    )

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
                condition=Q(description__length__gte=20),
                name="apartment_description_min_length",
            ),
            models.CheckConstraint(
                condition=Q(housing_type__in=HousingTypeChoices.values),
                name="apartment_housing_type_valid",
            ),
        ]

    def clean(self):
        if self.title:
            self.title = self.title.strip()

        if len(self.title) < 5:
            raise ValidationError(
                {"title": "Название должно содержать минимум 5 символов."}
            )

        if len(self.description.strip()) < 20:
            raise ValidationError({"description": "Описание слишком короткое."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} — {self.price}€"
