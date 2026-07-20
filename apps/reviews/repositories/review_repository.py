"""Repository module for handling Review database operations.

This module provides data access encapsulation for the Review model,
handling query existence checks, creation, and listing reviews by listing.
"""

from django.db.models import QuerySet

from apps.reviews.models import Review


class ReviewRepository:
    """Repository class encapsulating database queries and mutations for Review instances."""

    def exists_for_reservation(self, reservation_id: int) -> bool:
        """Check whether a review already exists for the specified reservation.

        Args:
            reservation_id (int): The ID of the reservation to check.

        Returns:
            bool: True if a review for this reservation exists, False otherwise.
        """
        return Review.objects.filter(reservation_id=reservation_id).exists()

    def create(self, listing, user, reservation, rating: int, comment: str) -> Review:
        """Create and persist a new review instance.

        Args:
            listing: The apartment listing being reviewed.
            user: The author user writing the review.
            reservation: The associated reservation instance.
            rating (int): The numerical rating score (typically 1 to 5).
            comment (str): The text commentary for the review.

        Returns:
            Review: The newly created Review instance.
        """
        return Review.objects.create(
            listing=listing,
            user=user,
            reservation=reservation,
            rating=rating,
            comment=comment,
        )

    def list_by_listing(self, listing_id: int) -> QuerySet:
        """Retrieve all reviews associated with a specific listing.

        Ordered by creation date descending.

        Args:
            listing_id (int): The ID of the listing.

        Returns:
            QuerySet: A queryset of Review instances with related user data prefetched.
        """
        return (
            Review.objects.select_related("user")
            .filter(listing_id=listing_id)
            .order_by("-created_at")
        )
