from django.db.models import QuerySet

from apps.reviews.models import Review


class ReviewRepository:
    def exists_for_reservation(self, reservation_id: int) -> bool:
        return Review.objects.filter(reservation_id=reservation_id).exists()

    def create(self, listing, user, reservation, rating: int, comment: str) -> Review:
        return Review.objects.create(
            listing=listing,
            user=user,
            reservation=reservation,
            rating=rating,
            comment=comment,
        )

    def list_by_listing(self, listing_id: int) -> QuerySet:
        return (
            Review.objects.select_related("user")
            .filter(listing_id=listing_id)
            .order_by("-created_at")
        )
