from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

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
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_range",
            ),
        ]

    def clean(self):
        if not self.reservation_id:
            raise ValidationError(
                {"reservation": "Отзыв должен быть привязан к бронированию."}
            )

        if self.rating is not None:
            if self.rating < 1 or self.rating > 5:
                raise ValidationError(
                    {"rating": "Оценка должна быть в диапазоне от 1 до 5."}
                )

        if self.reservation_id:
            if self.user_id and self.reservation.user_id != self.user_id:
                raise ValidationError(
                    {
                        "user": "Отзыв должен оставлять тот же пользователь, "
                        "что и указан в бронировании."
                    }
                )

        if self.listing_id and self.reservation.listing_id != self.listing_id:
            raise ValidationError(
                {"listing": "Жильё в отзыве должно совпадать с жильём из бронирования."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review #{self.id} listing={self.listing_id} rating={self.rating}"
