from rest_framework import serializers

from apps.listings.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "land", "city", "street", "postal_code"]
        read_only_fields = ["id"]
