
from django.conf import settings
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models import Q


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

        constraints = [
            models.CheckConstraint(
                condition=~Q(keyword=""),
                name="search_history_keyword_not_empty",
            ),
        ]

    def clean(self):
        if self.keyword:
            self.keyword = self.keyword.strip()

        if not self.keyword:
            raise ValidationError({"keyword": "Поисковый запрос не может быть пустым."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'search: "{self.keyword}" by user={self.user_id}'
