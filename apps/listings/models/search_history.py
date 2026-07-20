"""Search history model recording keyword searches for popularity tracking."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class SearchHistory(BaseModel):
    """A record of a search keyword entered by a user (or anonymous visitor)."""

    keyword = models.CharField(max_length=255)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="searches",
        null=True,
        blank=True,
    )

    class Meta:
        """Database table, indexes, and constraints for SearchHistory."""

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
        """Strip whitespace from the keyword and require it to be non-empty."""
        if self.keyword:
            self.keyword = self.keyword.strip()

        if not self.keyword:
            raise ValidationError({"keyword": "Search keyword cannot be empty."})

    def save(self, *args, **kwargs):
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a short label showing the keyword and searching user."""
        return f'search: "{self.keyword}" by user={self.user_id}'
