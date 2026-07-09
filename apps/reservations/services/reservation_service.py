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
    LessorStatusError,
    RenterCancelOnlyError,
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
    def __init__(self):
        self.repository = ReservationRepository()

    @transaction.atomic
    def create_reservation(self, user, validated_data: dict) -> Reservation:
        listing = validated_data["listing"]
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]

        self._validate_dates(start_date, end_date)

        if listing.owner_id == user.id:
            raise CannotBookOwnListingError()

        self.repository.lock_listing(listing.id)

        if self.repository.get_overlapping(listing, start_date, end_date).exists():
            raise DateOccupiedError()

        return self.repository.create(user, listing, start_date, end_date)

    def _validate_dates(self, start_date, end_date):
        today = timezone.now().date()
        if start_date < today or end_date < today:
            raise DateInPastError()
        if start_date >= end_date:
            raise StartDateGreaterEndDateError()

    @transaction.atomic
    def update_status(self, user, reservation_id: int, new_status: str) -> Reservation:
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        is_renter = reservation.user_id == user.id
        is_lessor = reservation.listing.owner_id == user.id
        if not (is_renter or is_lessor):
            raise ReservationPermissionDeniedError()

        if new_status not in ALLOWED_TRANSITIONS.get(reservation.status, set()):
            raise InvalidStatusTransitionError()

        if is_renter and not is_lessor:
            self._apply_renter_transition(reservation, new_status)
        else:
            self._apply_lessor_transition(reservation, new_status)

        reservation.status = new_status
        return self.repository.save(reservation)

    def _apply_renter_transition(self, reservation: Reservation, new_status: str):
        if new_status != StatusChoices.CANCELED:
            raise RenterCancelOnlyError()
        deadline = reservation.start_date - timedelta(days=CANCEL_DEADLINE_DAYS)
        if timezone.now().date() > deadline:
            raise CantBeCanceledError()

    def _apply_lessor_transition(self, reservation: Reservation, new_status: str):
        if new_status not in LESSOR_ALLOWED_STATUSES:
            raise LessorStatusError()

    def get_my_reservations(self, user) -> list:
        return list(self.repository.list_by_renter(user.id))

    def get_lessor_reservations(self, user) -> list:
        return list(self.repository.list_by_lessor(user.id))
