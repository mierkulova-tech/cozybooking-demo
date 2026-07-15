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
    @pytest.fixture
    def user_renter(self):
        return User.objects.create_user(
            name="Renter",
            email="renter@test.com",
            password="StrongPass123",
            role="RENTER",
        )

    @pytest.fixture
    def user_lessor(self):
        return User.objects.create_user(
            name="Lessor",
            email="lessor@test.com",
            password="StrongPass123",
            role="LESSOR",
        )

    @pytest.fixture
    def address(self):
        return Address.objects.create(
            land="Bayern", city="München", street="Teststr. 1", postal_code="80331"
        )

    @pytest.fixture
    def apartment(self, user_lessor, address):
        return Apartment.objects.create(
            owner=user_lessor,
            address=address,
            title="Test Apartment",
            description="Хорошее описание для тестов. Длинное и валидное описание квартиры.",
            price=1200,
            rooms=2,
            housing_type="STUDIO",
            is_active=True,
        )

    @pytest.fixture
    def reservation(self, apartment, user_renter):
        return Reservation.objects.create(
            listing=apartment,
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=15),
            status=StatusChoices.PENDING,
            price=6000,
        )

    def test_user_clean_email_lowercase(self):
        user = User(name="Test", email="TEST@EXAMPLE.COM", role="RENTER")
        user.clean()
        assert user.email == "test@example.com"

    def test_reservation_clean_valid_dates(self, apartment, user_renter):
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
        reservation = Reservation(
            listing=apartment,
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=5),
        )
        with pytest.raises(ValidationError):
            reservation.clean()

    def test_reservation_clean_cannot_book_own_listing(self, apartment, user_lessor):
        reservation = Reservation(
            listing=apartment,
            user=user_lessor,
            start_date=timezone.now().date() + timedelta(days=5),
            end_date=timezone.now().date() + timedelta(days=10),
        )
        with pytest.raises(ValidationError):
            reservation.clean()

    def test_review_clean_rating_range(self, apartment, user_renter, reservation):
        review = Review(
            listing=apartment,
            user=user_renter,
            reservation=reservation,
            rating=6,
            comment="Bad",
        )
        with pytest.raises(ValidationError):
            review.clean()

    def test_review_clean_owner_mismatch(
        self, apartment, user_renter, user_lessor, reservation
    ):
        review = Review(
            listing=apartment,
            user=user_lessor,
            reservation=reservation,
            rating=5,
            comment="Test",
        )
        with pytest.raises(
            ValidationError, match="Отзыв должен оставлять тот же пользователь"
        ):
            review.clean()

    def test_review_clean_listing_mismatch(self, apartment, user_renter, reservation):
        other_apartment = Apartment.objects.create(
            owner=apartment.owner,
            address=apartment.address,
            title="Other",
            description="Достаточно длинное описание для прохождения валидации в модели квартиры.",
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
        with pytest.raises(ValidationError, match="Жильё в отзыве должно совпадать"):
            review.clean()

    def test_review_clean_requires_reservation(self, apartment, user_renter):
        review = Review(
            listing=apartment,
            user=user_renter,
            reservation=None,
            rating=5,
        )
        with pytest.raises(ValidationError):
            review.clean()
