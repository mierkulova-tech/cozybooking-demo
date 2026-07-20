"""Django administration panel configuration for the reviews app.

This module registers the Review model with the Django admin interface
and configures list displays, filters, and search fields for administrative management.
"""

from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration interface for the Review model."""

    list_display = ["id", "listing", "user", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["listing__title", "comment"]
