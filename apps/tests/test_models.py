"""Tests for model clean methods, data normalization, and field validation constraints.

This module validates domain rules enforced by model-level clean methods,
including email normalization, date order logic, ownership rules, and review constraints.
"""

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.listings.models import Address, Apartment
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.models import Reservation
from apps.reviews.models import Review
from apps.users.models import User


@pytest.mark.django_db
class TestModelsCleanAndConstraints:
    """Test suite for validating model clean methods and database constraints."""

    @pytest.fixture
    def user_renter(self):
        """Fixture providing a user with the RENTER role."""
        return User.objects.create_user(
            name="Renter",
            email="renter@test.com",
            password="StrongPass123",
            role="RENTER",
        )

    @pytest.fixture
    def user_lessor(self):
        """Fixture providing a user with the LESSOR role."""
        return User.objects.create_user(
            name="Lessor",
            email="lessor@test.com",
            password="StrongPass123",
            role="LESSOR",
        )

    @pytest.fixture
    def address(self):
        """Fixture providing a standard test address."""
        return Address.objects.create(
            land="Bayern", city="München", street="Teststr. 1", postal_code="80331"
        )

    @pytest.fixture
    def apartment(self, user_lessor, address):
        """Fixture providing an active test apartment owned by the lessor."""
        return Apartment.objects.create(
            owner=user_lessor,
            address=address,
            title="Test Apartment",
            description=("Good description for tests. Long and valid apartment description."),
            price=1200,
            rooms=2,
            housing_type="STUDIO",
            is_active=True,
        )

    @pytest.fixture
    def reservation(self, apartment, user_renter):
        """Fixture providing a pending test reservation."""
        return Reservation.objects.create(
            listing=apartment,
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=15),
            status=StatusChoices.PENDING,
            price=6000,
        )

    def test_user_clean_email_lowercase(self):
        """Verify that user email addresses are normalized to lowercase during validation."""
        user = User(name="Test", email="TEST@EXAMPLE.COM", role="RENTER")
        user.clean()
        assert user.email == "test@example.com"

    def test_reservation_clean_valid_dates(self, apartment, user_renter):
        """Ensure that a reservation with valid start
        and end dates passes validation and saves successfully.
        """
        reservation = Reservation(
            listing=apartment,
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=5),
            end_date=timezone.now().date() + timedelta(days=10),
            status=StatusChoices.PENDING,
            price=5000,
        )
        reservation.clean()
        reservation.save()

    def test_reservation_clean_start_before_end(self, apartment, user_renter):
        """Ensure that a reservation where the start date
        is after the end date raises a validation error.
        """
        reservation = Reservation(
            listing=apartment,
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=5),
        )
        with pytest.raises(ValidationError):
            reservation.clean()

    def test_reservation_clean_cannot_book_own_listing(self, apartment, user_lessor):
        """Verify that lessors are prevented from
        booking their own apartment listings.
        """
        reservation = Reservation(
            listing=apartment,
            user=user_lessor,
            start_date=timezone.now().date() + timedelta(days=5),
            end_date=timezone.now().date() + timedelta(days=10),
        )
        with pytest.raises(ValidationError):
            reservation.clean()

    def test_review_clean_rating_range(self, apartment, user_renter, reservation):
        """Ensure that review ratings outside the
        allowed range raise a validation error.
        """
        review = Review(
            listing=apartment,
            user=user_renter,
            reservation=reservation,
            rating=6,
            comment="Bad",
        )
        with pytest.raises(ValidationError):
            review.clean()

    def test_review_clean_owner_mismatch(self, apartment, user_renter, user_lessor, reservation):
        """Verify that reviews must be submitted by
        the user who made the reservation.
        """
        review = Review(
            listing=apartment,
            user=user_lessor,
            reservation=reservation,
            rating=5,
            comment="Test",
        )
        with pytest.raises(ValidationError, match="The review must be left by the same user"):
            review.clean()

    def test_review_clean_listing_mismatch(self, apartment, user_renter, reservation):
        """Ensure that the review listing matches the
        listing associated with the reservation.
        """
        other_apartment = Apartment.objects.create(
            owner=apartment.owner,
            address=apartment.address,
            title="Other",
            description=("Sufficiently long description to pass apartment model validation."),
            price=1000,
            rooms=1,
            housing_type="ROOM",
        )
        review = Review(
            listing=other_apartment,
            user=user_renter,
            reservation=reservation,
            rating=5,
            comment="Mismatch",
        )
        with pytest.raises(
            ValidationError,
            match="The reviewed listing must match the reservation's listing",
        ):
            review.clean()

    def test_review_clean_requires_reservation(self, apartment, user_renter):
        """Verify that submitting a review without an
        attached reservation raises a validation error.
        """
        review = Review(
            listing=apartment,
            user=user_renter,
            reservation=None,
            rating=5,
        )
        with pytest.raises(ValidationError):
            review.clean()
