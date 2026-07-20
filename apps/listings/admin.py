"""Django admin configuration module for apartment listings, addresses, and history logs.

This module registers model administrators to manage apartments, addresses,
view histories, and search histories via the Django admin interface.
"""

from django.contrib import admin

from apps.listings.models import Address, Apartment, SearchHistory, ViewHistory


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    """Admin configuration for the Apartment model."""

    list_display = [
        "id",
        "title",
        "price",
        "rooms",
        "housing_type",
        "is_active",
        "owner",
    ]

    list_filter = ["housing_type", "is_active"]

    search_fields = ["title", "description"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for the Address model."""

    list_display = ["id", "city", "land", "postal_code"]

    search_fields = ["city", "land"]


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for the ViewHistory model."""

    list_display = ["id", "apartment", "user", "created_at"]


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for the SearchHistory model."""

    list_display = ["id", "keyword", "user", "created_at"]

    search_fields = ["keyword"]
