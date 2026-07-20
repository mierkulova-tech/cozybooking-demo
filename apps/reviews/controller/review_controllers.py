"""API views for creating and listing reviews."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reviews.dto.review_serializers import (
    ReviewCreateSerializer,
    ReviewResponseSerializer,
)
from apps.reviews.services.review_service import ReviewService


class ReviewCreateController(APIView):
    """Create a review for a completed reservation."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reviews"],
        summary="Create a review",
        description=(
            "Only after a completed stay (status CHECKED_IN). One review per reservation."
        ),
        request=ReviewCreateSerializer,
        responses={201: ReviewResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        """Create a review for the requesting user's completed reservation."""
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = ReviewService().create_review(request.user, serializer.validated_data)
        return Response(
            ReviewResponseSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class ListingReviewsController(APIView):
    """List all reviews for a given listing."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Reviews"],
        summary="Reviews for a listing",
        description="Fetch all reviews for a specific listing.",
        responses={200: ReviewResponseSerializer(many=True)},
    )
    def get(self, request, listing_id, *args, **kwargs):
        """Return all reviews associated with the given listing."""
        reviews = ReviewService().list_for_listing(listing_id)
        return Response(ReviewResponseSerializer(reviews, many=True).data)
