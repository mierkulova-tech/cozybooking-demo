from django.db import models

from apps.common.models.base import BaseModel


class Address(BaseModel):
    land = models.CharField(max_length=100, help_text="Федеральная земля (Bundesland)")
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = "addresses"
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["land"]),
        ]

    def __str__(self):
        return f"{self.postal_code} {self.city}, {self.land}".strip()
