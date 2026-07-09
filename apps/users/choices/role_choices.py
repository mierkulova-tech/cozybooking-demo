from django.db import models


class RoleChoices(models.TextChoices):
    RENTER = "RENTER", "Арендатор"
    LESSOR = "LESSOR", "Арендодатель"
