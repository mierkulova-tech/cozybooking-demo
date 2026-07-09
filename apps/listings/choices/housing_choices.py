from django.db import models


class HousingTypeChoices(models.TextChoices):
    APARTMENT = "APARTMENT", "Квартира"
    HOUSE = "HOUSE", "Дом"
    STUDIO = "STUDIO", "Студия"
    ROOM = "ROOM", "Комната"
