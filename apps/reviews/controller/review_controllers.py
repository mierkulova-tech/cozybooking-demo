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
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reviews"],
        summary="Создать отзыв",
        description="Только после завершенного проживания (статус CHECKED_IN). Один отзыв на бронь.",
        request=ReviewCreateSerializer,
        responses={201: ReviewResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = ReviewService().create_review(request.user, serializer.validated_data)
        return Response(
            ReviewResponseSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class ListingReviewsController(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Reviews"],
        summary="Отзывы по объявлению",
        description="Получить все отзывы для конкретного объявления.",
        responses={200: ReviewResponseSerializer(many=True)},
    )
    def get(self, request, listing_id, *args, **kwargs):
        reviews = ReviewService().list_for_listing(listing_id)
        return Response(ReviewResponseSerializer(reviews, many=True).data)
