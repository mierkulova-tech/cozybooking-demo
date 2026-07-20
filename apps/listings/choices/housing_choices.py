"""Housing type choices for apartment listings."""

from django.db import models


class HousingTypeChoices(models.TextChoices):
    """Available housing types for apartments."""

    APARTMENT = "APARTMENT", "Apartment"
    HOUSE = "HOUSE", "House"
    STUDIO = "STUDIO", "Studio"
    ROOM = "ROOM", "Room"
