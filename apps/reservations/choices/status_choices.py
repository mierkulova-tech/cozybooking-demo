from django.db import models


class StatusChoices(models.TextChoices):
    PENDING = "PENDING", "Ожидает подтверждения"

    CONFIRMED = "CONFIRMED", "Подтверждено"

    REJECTED = "REJECTED", "Отклонено"

    CHECKED_IN = "CHECKED_IN", "Заселение состоялось"

    CANCELED = "CANCELED", "Отменено"
