from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class SearchHistory(BaseModel):
    keyword = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="searches",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "search_history"
        indexes = [
            models.Index(fields=["keyword"]),
        ]

    def __str__(self):
        return f'search: "{self.keyword}" by user={self.user_id}'
