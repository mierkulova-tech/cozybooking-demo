"""Business logic for reservations.

Handles creating, confirming, checking in, and canceling reservations.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.common.utils.content import check_content_helper
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.errors.reservations_errors import (
    CannotBookOwnListingError,
    CantBeCanceledError,
    DateInPastError,
    DateOccupiedError,
    InvalidStatusTransitionError,
    ReservationPermissionDeniedError,
    StartDateGreaterEndDateError,
)
from apps.reservations.models import Reservation
from apps.reservations.repositories.reservation_repository import ReservationRepository

CANCEL_DEADLINE_DAYS = 2

LESSOR_ALLOWED_STATUSES = {
    StatusChoices.CONFIRMED,
    StatusChoices.REJECTED,
    StatusChoices.CHECKED_IN,
}


ALLOWED_TRANSITIONS = {
    StatusChoices.PENDING: {
        StatusChoices.CONFIRMED,
        StatusChoices.REJECTED,
        StatusChoices.CANCELED,
    },
    StatusChoices.CONFIRMED: {
        StatusChoices.CHECKED_IN,
        StatusChoices.CANCELED,
    },
    StatusChoices.CHECKED_IN: set(),
    StatusChoices.REJECTED: set(),
    StatusChoices.CANCELED: set(),
}


class ReservationService:
    """Coordinates reservation creation and status transitions.

    Enforces ownership, permissions, and the allowed status-transition graph.
    """

    def __init__(self):
        """Initialize the reservation service with its repository."""
        self.repository = ReservationRepository()

    def _ensure_transition_allowed(
        self,
        current_status,
        new_status,
        error_class=InvalidStatusTransitionError,
        message=None,
    ):
        """Check the requested status change against ALLOWED_TRANSITIONS.

        Args:
            current_status: The reservation's current status.
            new_status: The status being transitioned to.
            error_class: Exception class to raise if the transition is not allowed.
            message: Optional custom error detail.

        Raises:
            error_class: If new_status is not reachable from current_status.
        """
        allowed = ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            if message:
                raise error_class(message)
            raise error_class()

    @transaction.atomic
    def create_reservation(self, user, validated_data: dict) -> Reservation:
        """Create a reservation after validating dates, ownership, and availability.

        Locks the listing row for the duration of the transaction to prevent
        a race condition between two overlapping bookings (TOCTOU).

        Args:
            user: The renter making the reservation.
            validated_data: Validated data including "listing", "start_date",
                and "end_date".

        Returns:
            The newly created Reservation instance.

        Raises:
            DateInPastError: If start_date or end_date is in the past.
            StartDateGreaterEndDateError: If start_date is not before end_date.
            CannotBookOwnListingError: If the user owns the listing.
            DateOccupiedError: If the listing is already booked for an
                overlapping date range.
        """
        listing = validated_data["listing"]
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]

        self._validate_dates(start_date, end_date)

        if listing.owner_id == user.id:
            raise CannotBookOwnListingError()

        listing = self.repository.lock_listing(listing.id)

        if self.repository.get_overlapping(listing, start_date, end_date).exists():
            raise DateOccupiedError()

        nights = (end_date - start_date).days
        total_price = listing.price * nights

        return self.repository.create(
            user=user,
            listing=listing,
            start_date=start_date,
            end_date=end_date,
            price=total_price,
        )

    def _validate_dates(self, start_date, end_date):
        today = timezone.now().date()
        if start_date < today or end_date < today:
            raise DateInPastError()
        if start_date >= end_date:
            raise StartDateGreaterEndDateError()

    @transaction.atomic
    def confirm_reservation(self, user, reservation_id: int) -> Reservation:
        """Confirm a pending reservation (lessor action)."""
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        if reservation.listing.owner_id != user.id:
            raise ReservationPermissionDeniedError()

        self._ensure_transition_allowed(reservation.status, StatusChoices.CONFIRMED)

        reservation.status = StatusChoices.CONFIRMED
        return self.repository.save(reservation)

    @transaction.atomic
    def check_in_reservation(self, user, reservation_id: int) -> Reservation:
        """Mark a reservation as checked-in."""
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        if reservation.listing.owner_id != user.id:
            raise ReservationPermissionDeniedError()

        self._ensure_transition_allowed(reservation.status, StatusChoices.CHECKED_IN)

        today = timezone.now().date()
        if not (reservation.start_date <= today <= reservation.end_date):
            raise InvalidStatusTransitionError(
                detail="Check-in is only possible during the stay dates."
            )

        reservation.status = StatusChoices.CHECKED_IN
        return self.repository.save(reservation)

    @transaction.atomic
    def cancel_reservation(self, user, reservation_id: int) -> Reservation:
        """Cancel a reservation adhering to time and status rules."""
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        is_renter = reservation.user_id == user.id
        is_lessor = reservation.listing.owner_id == user.id

        if not (is_renter or is_lessor):
            raise ReservationPermissionDeniedError()

        self._ensure_transition_allowed(
            reservation.status,
            StatusChoices.CANCELED,
            error_class=CantBeCanceledError,
            message="This reservation can no longer be canceled — "
            "it has already started (CHECKED_IN).",
        )

        if is_renter and not is_lessor:
            deadline = reservation.start_date - timedelta(days=CANCEL_DEADLINE_DAYS)
            if timezone.now().date() > deadline:
                raise CantBeCanceledError(
                    f"Cancellation is only allowed up to {CANCEL_DEADLINE_DAYS}"
                    f"days before check-in."
                )

        reservation.status = StatusChoices.CANCELED
        return self.repository.save(reservation)

    def get_my_reservations(self, user) -> list:
        """Retrieve all reservations made by the specified renter user."""
        return list(self.repository.list_by_renter(user.id))

    def get_lessor_reservations(self, user) -> list:
        """Retrieve all reservations for properties owned by the authenticated lessor."""
        return list(self.repository.list_by_lessor(user.id))
