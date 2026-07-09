from rest_framework import serializers

from apps.reviews.models import Review


class ReviewCreateSerializer(serializers.Serializer):
    reservation = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True, required=False, default="")


class ReviewResponseSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "listing", "author", "rating", "comment", "created_at"]
