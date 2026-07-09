from decimal import Decimal

from rest_framework import serializers

from apps.listings.choices.housing_choices import HousingTypeChoices
from apps.listings.constants.filter_constants import ALLOWED_ORDER_FIELDS


class ListingQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    price_min = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=Decimal("0")
    )
    price_max = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=Decimal("0")
    )
    rooms_min = serializers.IntegerField(required=False, min_value=Decimal("0"))
    rooms_max = serializers.IntegerField(required=False, min_value=Decimal("0"))
    housing_type = serializers.ChoiceField(
        choices=HousingTypeChoices.choices, required=False, allow_blank=True
    )
    order = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1)

    def validate_order(self, value):
        if value and value not in ALLOWED_ORDER_FIELDS:
            raise serializers.ValidationError(
                f"Допустимые значения: {', '.join(sorted(ALLOWED_ORDER_FIELDS))}."
            )
        return value
