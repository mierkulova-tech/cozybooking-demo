"""Status choices for reservations."""

from django.db import models


class StatusChoices(models.TextChoices):
    """Available reservation lifecycle statuses."""

    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    REJECTED = "REJECTED", "Rejected"
    CHECKED_IN = "CHECKED_IN", "Checked in"
    CANCELED = "CANCELED", "Canceled"
