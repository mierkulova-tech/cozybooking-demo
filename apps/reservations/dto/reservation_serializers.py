from rest_framework import serializers

from apps.listings.models import Apartment
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.models import Reservation


class ReservationCreateSerializer(serializers.Serializer):
    listing = serializers.PrimaryKeyRelatedField(
        queryset=Apartment.objects.filter(is_active=True)
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ReservationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=StatusChoices.choices)


class ReservationResponseSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source="listing.title", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "listing",
            "listing_title",
            "user",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]
