"""Edge case tests for reservation restrictions,
review limits, and apartment availability toggles.

This module validates error handling and business constraints for inactive apartments,
duplicate reviews, and availability toggles.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.listings.services.apartment_service import ApartmentService
from apps.reservations.services.reservation_service import ReservationService
from apps.reviews.services.review_service import ReviewService


@pytest.fixture
def apartment_inactive(user_lessor, address):
    """Fixture providing an inactive apartment instance."""
    from apps.listings.models import Apartment

    return Apartment.objects.create(
        owner=user_lessor,
        address=address,
        title="Inactive Apt",
        description=(
            "Spacious and bright studio with modern renovation, "
            "kitchen, bathroom, and balcony. Fully furnished."
        ),
        price=1000,
        rooms=2,
        housing_type="STUDIO",
        is_active=False,
    )


@pytest.mark.django_db
class TestEdgeCases:
    """Test suite for application edge cases and error conditions."""

    def test_reservation_service_cannot_book_inactive(self, apartment_inactive, user_renter):
        """Ensure that attempting to book an inactive apartment raises an exception."""
        service = ReservationService()
        with pytest.raises(Exception):
            service.create_reservation(
                user_renter,
                {
                    "listing": apartment_inactive.id,
                    "start_date": timezone.now().date() + timedelta(days=5),
                    "end_date": timezone.now().date() + timedelta(days=10),
                },
            )

    def test_review_service_already_reviewed(self, reservation_checked_in, user_renter):
        """Ensure that submitting a second review
        for the same reservation raises an exception.
        """
        service = ReviewService()
        service.create_review(user_renter, {"reservation": reservation_checked_in.id, "rating": 5})

        with pytest.raises(Exception):
            service.create_review(
                user_renter, {"reservation": reservation_checked_in.id, "rating": 4}
            )

    def test_apartment_service_toggle_availability(self, apartment, user_lessor):
        """Verify that toggling apartment availability
        successfully flips its active status.
        """
        service = ApartmentService()
        toggled = service.toggle_availability(user_lessor, apartment.id)
        assert toggled.is_active != apartment.is_active
