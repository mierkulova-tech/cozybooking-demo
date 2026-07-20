"""URL routing configuration for the reviews application.

This module defines URL patterns for creating reviews and listing reviews
associated with specific property listings.
"""

from django.urls import path

from apps.reviews.controller.review_controllers import (
    ListingReviewsController,
    ReviewCreateController,
)

app_name = "reviews"

urlpatterns = [
    path("", ReviewCreateController.as_view(), name="create"),
    path(
        "listing/<int:listing_id>/",
        ListingReviewsController.as_view(),
        name="by-listing",
    ),
]
