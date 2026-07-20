"""Business logic for creating and listing apartment reviews."""

from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.repositories.reservation_repository import ReservationRepository
from apps.reviews.errors.reviews_errors import (
    AlreadyReviewedError,
    NotReservationOwnerError,
    ReservationNotFoundError,
    StayNotCompletedError,
)
from apps.reviews.models import Review
from apps.reviews.repositories.review_repository import ReviewRepository


class ReviewService:
    """Coordinates review creation with reservation-based eligibility checks."""

    def __init__(self):
        """Initialize the review service with review and reservation repositories."""
        self.repository = ReviewRepository()
        self.reservation_repository = ReservationRepository()

    def create_review(self, user, validated_data: dict) -> Review:
        """Create a review for a stay in progress or completed, enforcing eligibility rules.

        A review can only be left by the renter who made the reservation,
        only after they have actually checked in (status CHECKED_IN), and
        only once per reservation.

        Args:
            user: The user submitting the review (must be the renter).
            validated_data: Validated review data, including "reservation",
                "rating", and optionally "comment".

        Returns:
            The newly created Review instance.

        Raises:
            ReservationNotFoundError: If the reservation does not exist.
            NotReservationOwnerError: If the user is not the renter on this
                reservation.
            StayNotCompletedError: If the guest hasn't checked in yet
                (status is not CHECKED_IN).
            AlreadyReviewedError: If a review already exists for this
                reservation.
        """
        reservation = self.reservation_repository.get_by_id(validated_data["reservation"])
        if reservation is None:
            raise ReservationNotFoundError()

        if reservation.user_id != user.id:
            raise NotReservationOwnerError()

        if reservation.status != StatusChoices.CHECKED_IN:
            raise StayNotCompletedError()

        if self.repository.exists_for_reservation(reservation.id):
            raise AlreadyReviewedError()

        return self.repository.create(
            listing=reservation.listing,
            user=user,
            reservation=reservation,
            rating=validated_data["rating"],
            comment=validated_data.get("comment", ""),
        )

    def list_for_listing(self, listing_id: int) -> list:
        """Return all reviews left for the given listing."""
        return list(self.repository.list_by_listing(listing_id))
