from django.urls import path

from apps.listings.controller.apartment_controllers import (
    ListingAvailabilityController,
    ListingDetailController,
    ListingListController,
    MyListingsController,
    PopularSearchesController,
)

app_name = "listings"

urlpatterns = [
    path("", ListingListController.as_view(), name="list"),
    path("my/", MyListingsController.as_view(), name="my"),
    path(
        "popular-searches/",
        PopularSearchesController.as_view(),
        name="popular-searches",
    ),
    path("<int:apartment_id>/", ListingDetailController.as_view(), name="detail"),
    path(
        "<int:apartment_id>/availability/",
        ListingAvailabilityController.as_view(),
        name="availability",
    ),
]
