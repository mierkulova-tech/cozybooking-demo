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
    def __init__(self):
        self.repository = ReviewRepository()
        self.reservation_repository = ReservationRepository()

    def create_review(self, user, validated_data: dict) -> Review:
        reservation = self.reservation_repository.get_by_id(
            validated_data["reservation"]
        )
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
        return list(self.repository.list_by_listing(listing_id))
