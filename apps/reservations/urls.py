from django.urls import path

from apps.reservations.controller.reservation_controllers import (
    LessorReservationsController,
    MyReservationsController,
    ReservationCreateController,
    ReservationStatusController,
)

app_name = "reservations"

urlpatterns = [
    path("", ReservationCreateController.as_view(), name="create"),
    path("my/", MyReservationsController.as_view(), name="my"),
    path("incoming/", LessorReservationsController.as_view(), name="incoming"),
    path(
        "<int:reservation_id>/status/",
        ReservationStatusController.as_view(),
        name="status",
    ),
]
