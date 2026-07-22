"""Error classes for the listings application."""

from rest_framework import status

from apps.common.exceptions.base import (
    ApplicationError,
    NoContentError,
    PermissionDeniedError,
)


class ListingNotFoundError(NoContentError):
    """Raised when the requested listing does not exist."""

    default_detail = "Listing not found."
    default_code = "listing_not_found"


class NotListingOwnerError(PermissionDeniedError):
    """Raised when a user tries to manage a listing they do not own."""

    default_detail = "You can only manage your own listings."
    default_code = "not_listing_owner"


class PageParameterError(ApplicationError):
    """Raised when an invalid pagination parameter is provided."""

    default_detail = "Invalid pagination parameter."
    default_code = "invalid_page_parameter"


class ListingHasReservationsError(ApplicationError):
    """Raised when trying to delete a listing that has existing reservations."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "This listing has active reservations and cannot be deleted."
    default_code = "listing_has_reservations"
