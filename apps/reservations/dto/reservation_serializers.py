"""Reservation serialization modules for the cozybooking project.

This module provides serializers for validating reservation creation input data,
representing reservation response payloads, and handling status updates.
"""

from rest_framework import serializers

from apps.listings.models import Apartment
from apps.reservations.models import Reservation


class ReservationCreateSerializer(serializers.Serializer):
    """Serializer for validating incoming reservation creation requests."""

    listing = serializers.PrimaryKeyRelatedField(queryset=Apartment.objects.filter(is_active=True))
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        """Validate that the reservation start date precedes the end date.

        Args:
            data (dict): The field values to validate.

        Returns:
            dict: The validated data dictionary.

        Raises:
            serializers.ValidationError: If start_date is greater than or equal to end_date.
        """
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError("Дата окончания должна быть позже начала.")
        return data


class ReservationResponseSerializer(serializers.ModelSerializer):
    """Serializer for transforming Reservation model instances into API response payloads."""

    listing_title = serializers.CharField(source="listing.title", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        """Meta options for ReservationResponseSerializer."""

        model = Reservation
        fields = [
            "id",
            "listing",
            "listing_title",
            "user",
            "user_name",
            "start_date",
            "end_date",
            "price",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at", "price"]


class ReservationStatusUpdateSerializer(serializers.Serializer):
    """Serializer placeholder for handling reservation status transition payloads."""

    pass
