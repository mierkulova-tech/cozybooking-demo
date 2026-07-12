
from django.contrib import admin

from apps.reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "user", "start_date", "end_date", "status"]

    list_filter = ["status"]

    search_fields = ["listing__title", "user__email"]
