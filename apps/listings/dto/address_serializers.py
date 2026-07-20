"""Serializer module for address model objects.

This module provides DRF serialization for the Address model,
exposing fields such as land, city, street, and postal code.
"""

from rest_framework import serializers

from apps.listings.models import Address


class AddressSerializer(serializers.ModelSerializer):
    """Serializer class for serializing and deserializing Address instances."""

    class Meta:
        """Meta options for the AddressSerializer."""

        model = Address

        fields = ["id", "land", "city", "street", "postal_code"]

        read_only_fields = ["id"]
