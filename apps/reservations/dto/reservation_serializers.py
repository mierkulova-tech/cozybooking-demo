from rest_framework import serializers

from apps.listings.models import Apartment
from apps.reservations.models import Reservation


class ReservationCreateSerializer(serializers.Serializer):
    listing = serializers.PrimaryKeyRelatedField(
        queryset=Apartment.objects.filter(is_active=True)
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "Дата окончания должна быть позже начала."
            )
        return data


class ReservationResponseSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
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
    pass
