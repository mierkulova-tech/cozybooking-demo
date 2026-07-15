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
        validators=[
            MinValueValidator(Decimal("0.01"), message="Цена должна быть больше нуля.")
        ],
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
        super().clean()

        current_date = timezone.now().date()

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    {
                        "end_date": "Дата окончания бронирования должна быть позже даты начала."
                    }
                )

        if self.user_id and self.listing_id:
            if self.listing.owner_id == self.user_id:
                raise ValidationError(
                    {"user": "Вы не можете забронировать свое собственное жилье."}
                )

        if not self.pk:
            if self.start_date and self.start_date < current_date:
                raise ValidationError(
                    {"start_date": "Нельзя создать бронирование в прошлом."}
                )
        else:
            original = Reservation.objects.get(pk=self.pk)
            if (
                original.start_date != self.start_date
                and self.start_date < current_date
            ):
                raise ValidationError(
                    {"start_date": "Нельзя перенести бронирование на дату в прошлом."}
                )

        if self.start_date and (self.start_date - current_date).days > 365:
            raise ValidationError(
                {"start_date": "Бронирование возможно максимум на 1 год вперёд."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation #{self.id} listing={self.listing_id} [{self.status}]"
