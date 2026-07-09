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
    def get_by_id(self, reservation_id: int) -> Reservation | None:
        return (
            Reservation.objects.select_related("listing", "listing__owner", "user")
            .filter(id=reservation_id)
            .first()
        )

    def get_overlapping(self, listing, start_date, end_date) -> QuerySet:

        return Reservation.objects.filter(
            Q(listing=listing)
            & Q(start_date__lt=end_date)
            & Q(end_date__gt=start_date)
            & ~Q(status__in=[StatusChoices.CANCELED, StatusChoices.REJECTED])
        )

    def lock_listing(self, listing_id: int) -> Apartment:

        return Apartment.objects.select_for_update().get(id=listing_id)

    def create(self, user, listing, start_date, end_date) -> Reservation:
        return Reservation.objects.create(
            user=user,
            listing=listing,
            start_date=start_date,
            end_date=end_date,
            status=StatusChoices.PENDING,
        )

    def save(self, reservation: Reservation) -> Reservation:
        reservation.save()
        return reservation

    def list_by_renter(self, user_id: int) -> QuerySet:
        return (
            Reservation.objects.select_related("listing")
            .filter(user_id=user_id)
            .annotate(status_order=_STATUS_ORDER)
            .order_by("status_order", "start_date")
        )

    def list_by_lessor(self, lessor_id: int) -> QuerySet:
        return (
            Reservation.objects.select_related("listing", "user")
            .filter(listing__owner_id=lessor_id)
            .annotate(status_order=_STATUS_ORDER)
            .order_by("status_order", "start_date")
        )
