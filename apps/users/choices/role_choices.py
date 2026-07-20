"""Role choices for user accounts."""

from django.db import models


class RoleChoices(models.TextChoices):
    """Available user roles in the system."""

    RENTER = "RENTER", "Renter"
    LESSOR = "LESSOR", "Lessor"
