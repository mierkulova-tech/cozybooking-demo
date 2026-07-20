"""Error classes for the reviews application."""

from apps.common.exceptions.base import (
    ApplicationError,
    NoContentError,
    PermissionDeniedError,
)


class ReservationNotFoundError(NoContentError):
    """Raised when the referenced reservation does not exist."""

    default_detail = "Reservation not found."
    default_code = "reservation_not_found"


class NotReservationOwnerError(PermissionDeniedError):
    """Raised when someone other than the reservation's renter tries to leave a review."""

    default_detail = "Only the renter who made the reservation can leave a review."
    default_code = "not_reservation_owner"


class StayNotCompletedError(ApplicationError):
    """Raised when a review is attempted before the stay has taken place."""

    default_detail = "A review can only be left after the stay has taken place."
    default_code = "stay_not_completed"


class AlreadyReviewedError(ApplicationError):
    """Raised when a reservation has already been reviewed."""

    default_detail = "A review for this reservation has already been submitted."
    default_code = "already_reviewed"
