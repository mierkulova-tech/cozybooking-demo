"""Error classes for the reservations application."""

from apps.common.exceptions.base import ApplicationError, PermissionDeniedError


class DateInPastError(ApplicationError):
    """Raised when reservation dates are set in the past."""

    default_detail = "Reservation dates cannot be in the past."
    default_code = "date_in_past"


class StartDateGreaterEndDateError(ApplicationError):
    """Raised when the check-in date is later than or equal to the check-out date."""

    default_detail = "The check-in date must be earlier than the check-out date."
    default_code = "start_date_greater_end_date"


class DateOccupiedError(ApplicationError):
    """Raised when the listing is already booked for the selected dates."""

    default_detail = "The listing is already booked for the selected dates."
    default_code = "date_is_occupied"


class CannotBookOwnListingError(ApplicationError):
    """Raised when a user attempts to book their own listing."""

    default_detail = "You cannot book your own listing."
    default_code = "cannot_book_own_listing"


class ReservationPermissionDeniedError(PermissionDeniedError):
    """Raised when a user does not have permission to modify a reservation."""

    default_detail = "You do not have permission to modify this reservation."
    default_code = "reservation_permission_denied"


class CantBeCanceledError(ApplicationError):
    """Raised when a reservation cannot be canceled in its current state."""

    default_detail = "This reservation cannot be canceled."
    default_code = "cant_be_canceled"


class InvalidStatusTransitionError(ApplicationError):
    """Raised when a reservation status change is not allowed from its current state."""

    default_detail = "This status transition is not allowed."
    default_code = "invalid_status_transition"
