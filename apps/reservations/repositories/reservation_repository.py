"""Repository module for handling Reservation database operations.

This module provides data access encapsulation for the Reservation model,
managing queries, database locking, creation, status-ordered listings for renters and lessors,
and overlap checking.
"""

from django.db.models import Case, IntegerField, Q, QuerySet, When

from apps.listings.models import Apartment
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.models import Reservation

_STATUS_ORDER = Case(
    When(status=StatusChoices.PENDING, then=0),
    When(status=StatusChoices.CONFIRMED, then=1),
    When(status=StatusChoices.CHECKED_IN, then=2),
    When(status=StatusChoices.REJECTED, then=3),
    When(status=StatusChoices.CANCELED, then=4),
    default=5,
    output_field=IntegerField(),
)


class ReservationRepository:
    """Repository class encapsulating database queries and mutations for Reservation instances."""

    def get_by_id(self, reservation_id: int) -> Reservation | None:
        """Retrieve a reservation by its ID with related listing, owner, and user prefetched.

        Args:
            reservation_id (int): The ID of the reservation.

        Returns:
            Reservation | None: The Reservation instance if found, otherwise None.
        """
        return (
            Reservation.objects.select_related("listing", "listing__owner", "user")
            .filter(id=reservation_id)
            .first()
        )

    def get_by_id_for_update(self, reservation_id: int) -> Reservation | None:
        """Retrieve a reservation by its ID with a row-level lock.

        For use inside an atomic transaction to prevent concurrent status
        changes on the same reservation.

        Args:
            reservation_id (int): The ID of the reservation.

        Returns:
            Reservation | None: The locked Reservation instance if found,
                otherwise None.
        """
        return (
            Reservation.objects.select_related("listing", "listing__owner", "user")
            .select_for_update()
            .filter(id=reservation_id)
            .first()
        )

    def get_overlapping(self, listing, start_date, end_date) -> QuerySet:
        """Retrieve active overlapping reservations for a given listing and date range.

        Args:
            listing: The Apartment listing instance.
            start_date: The proposed start date.
            end_date: The proposed end date.

        Returns:
            QuerySet: A queryset of overlapping reservations excluding canceled and rejected ones.
        """
        return Reservation.objects.filter(
            Q(listing=listing)
            & Q(start_date__lt=end_date)
            & Q(end_date__gt=start_date)
            & ~Q(status__in=[StatusChoices.CANCELED, StatusChoices.REJECTED])
        )

    def lock_listing(self, listing_id: int) -> Apartment:
        """Acquire a row-level database lock on a listing for concurrency safety.

        Args:
            listing_id (int): The ID of the listing to lock.

        Returns:
            Apartment: The locked Apartment instance.
        """
        return Apartment.objects.select_for_update().get(id=listing_id)

    def create(self, user, listing, start_date, end_date, price) -> Reservation:
        """Create and persist a new reservation with a PENDING status.

        Args:
            user: The user making the reservation.
            listing: The apartment listing being reserved.
            start_date: The check-in start date.
            end_date: The check-out end date.
            price (Decimal): The total calculated reservation price.

        Returns:
            Reservation: The newly created Reservation instance.
        """
        return Reservation.objects.create(
            user=user,
            listing=listing,
            start_date=start_date,
            end_date=end_date,
            price=price,
            status=StatusChoices.PENDING,
        )

    def save(self, reservation: Reservation) -> Reservation:
        """Save modifications to an existing Reservation instance to the database.

        Args:
            reservation (Reservation): The Reservation instance to save.

        Returns:
            Reservation: The updated Reservation instance.
        """
        reservation.save()
        return reservation

    def list_by_renter(self, user_id: int) -> QuerySet:
        """Retrieve all reservations made by a specific renter.

        Ordered by status priority and start date.

        Args:
            user_id (int): The ID of the renter user.

        Returns:
            QuerySet: A queryset of reservations annotated with custom status ordering.
        """
        return (
            Reservation.objects.select_related("listing")
            .filter(user_id=user_id)
            .annotate(status_order=_STATUS_ORDER)
            .order_by("status_order", "start_date")
        )

    def list_by_lessor(self, lessor_id: int) -> QuerySet:
        """Retrieve all reservations on listings owned by a specific lessor.

        Ordered by status priority and start date.

        Args:
            lessor_id (int): The ID of the lessor owner.

        Returns:
            QuerySet: A queryset of reservations annotated with custom status ordering.
        """
        return (
            Reservation.objects.select_related("listing", "user")
            .filter(listing__owner_id=lessor_id)
            .annotate(status_order=_STATUS_ORDER)
            .order_by("status_order", "start_date")
        )
