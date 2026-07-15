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
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        if reservation.listing.owner_id != user.id:
            raise ReservationPermissionDeniedError()

        if reservation.status != StatusChoices.PENDING:
            raise InvalidStatusTransitionError()

        reservation.status = StatusChoices.CONFIRMED
        return self.repository.save(reservation)

    @transaction.atomic
    def check_in_reservation(self, user, reservation_id: int) -> Reservation:
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        if reservation.listing.owner_id != user.id:
            raise ReservationPermissionDeniedError()

        if reservation.status != StatusChoices.CONFIRMED:
            raise InvalidStatusTransitionError()

        today = timezone.now().date()
        if not (reservation.start_date <= today <= reservation.end_date):
            raise InvalidStatusTransitionError(
                detail="Check-in возможен только в дни пребывания."
            )

        reservation.status = StatusChoices.CHECKED_IN
        return self.repository.save(reservation)

    @transaction.atomic
    def cancel_reservation(self, user, reservation_id: int) -> Reservation:
        reservation = self.repository.get_by_id(reservation_id)
        check_content_helper(reservation)

        is_renter = reservation.user_id == user.id
        is_lessor = reservation.listing.owner_id == user.id

        if not (is_renter or is_lessor):
            raise ReservationPermissionDeniedError()

        if reservation.status == StatusChoices.CHECKED_IN:
            raise CantBeCanceledError(
                "Нельзя отменить бронирование, которое уже началось (CHECKED_IN)."
            )

        if is_renter and not is_lessor:
            deadline = reservation.start_date - timedelta(days=CANCEL_DEADLINE_DAYS)
            if timezone.now().date() > deadline:
                raise CantBeCanceledError(
                    f"Отмена возможна не позднее чем за {CANCEL_DEADLINE_DAYS} дней до заезда."
                )

        reservation.status = StatusChoices.CANCELED
        return self.repository.save(reservation)

    def get_my_reservations(self, user) -> list:
        return list(self.repository.list_by_renter(user.id))

    def get_lessor_reservations(self, user) -> list:
        return list(self.repository.list_by_lessor(user.id))
