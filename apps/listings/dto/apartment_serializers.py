"""Serializer module for apartment creation, updates, and responses.

This module defines Django REST Framework serializers to validate input payloads
for creating and updating apartments, as well as serializing apartment details
for API responses.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.listings.choices.housing_choices import HousingTypeChoices
from apps.listings.dto.address_serializers import AddressSerializer
from apps.listings.models import Apartment


class ApartmentCreateSerializer(serializers.Serializer):
    """Serializer for validating payload data when creating a new apartment listing."""

    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))

    rooms = serializers.IntegerField(min_value=1)

    housing_type = serializers.ChoiceField(choices=HousingTypeChoices.choices)

    address = AddressSerializer()


class ApartmentUpdateSerializer(serializers.Serializer):
    """Serializer for validating payload data.

    Used when partially or fully updating an apartment listing.
    """

    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01"), required=False
    )
    rooms = serializers.IntegerField(min_value=1, required=False)
    housing_type = serializers.ChoiceField(choices=HousingTypeChoices.choices, required=False)
    is_active = serializers.BooleanField(required=False)

    address = AddressSerializer(required=False)


class ApartmentResponseSerializer(serializers.ModelSerializer):
    """Serializer for serializing Apartment model instances into API responses."""

    address = AddressSerializer(read_only=True)

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    owner_name = serializers.CharField(source="owner.name", read_only=True)
    views_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta options for ApartmentResponseSerializer."""

        model = Apartment
        fields = [
            "id",
            "title",
            "description",
            "price",
            "rooms",
            "housing_type",
            "is_active",
            "address",
            "owner_id",
            "owner_name",
            "created_at",
            "views_count",
        ]
