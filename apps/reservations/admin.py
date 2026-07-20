"""Django administration panel configuration for the reservations app.

This module registers the Reservation model with the Django admin interface
and configures list displays, filters, and search fields for administrative management.
"""

from django.contrib import admin

from apps.reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin configuration interface for the Reservation model."""

    list_display = ["id", "listing", "user", "start_date", "end_date", "status"]

    list_filter = ["status"]

    search_fields = ["listing__title", "user__email"]
