"""Review serialization modules for the cozybooking project.

This module contains serializers for handling review creation input validation
and serializing review response data with author details.
"""

from rest_framework import serializers

from apps.reviews.models import Review


class ReviewCreateSerializer(serializers.Serializer):
    """Serializer for validating incoming review creation payload data."""

    reservation = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True, required=False, default="")


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for transforming Review model instances into API response payloads."""

    author = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        """Meta options for ReviewResponseSerializer."""

        model = Review
        fields = ["id", "listing", "author", "rating", "comment", "created_at"]
