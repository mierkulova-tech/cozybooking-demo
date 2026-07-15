from django.urls import path

from apps.reservations.controller.reservation_controllers import (
    LessorReservationsController,
    MyReservationsController,
    ReservationCancelController,
    ReservationCheckInController,
    ReservationConfirmController,
    ReservationCreateController,
)

app_name = "reservations"

urlpatterns = [
    path("", ReservationCreateController.as_view(), name="create"),
    path("my/", MyReservationsController.as_view(), name="my-reservations"),
    path("lessor/", LessorReservationsController.as_view(), name="lessor-reservations"),
    path(
        "<int:reservation_id>/confirm/",
        ReservationConfirmController.as_view(),
        name="confirm",
    ),
    path(
        "<int:reservation_id>/check-in/",
        ReservationCheckInController.as_view(),
        name="check-in",
    ),
    path(
        "<int:reservation_id>/cancel/",
        ReservationCancelController.as_view(),
        name="cancel",
    ),
]
