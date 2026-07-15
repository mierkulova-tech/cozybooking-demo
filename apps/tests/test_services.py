from datetime import timedelta

import pytest
from django.utils import timezone

from apps.listings.services.apartment_service import ApartmentService
from apps.reservations.services.reservation_service import ReservationService
from apps.reviews.services.review_service import ReviewService
from apps.users.services.user_service import UserService


@pytest.mark.django_db
class TestBusinessLogic:
    @pytest.fixture
    def user_lessor(self):
        from apps.users.models import User

        return User.objects.create_user(
            name="Lessor",
            email="lessor@test.com",
            password="StrongPass123",
            role="LESSOR",
        )

    @pytest.fixture
    def user_renter(self):
        from apps.users.models import User

        return User.objects.create_user(
            name="Renter",
            email="renter@test.com",
            password="StrongPass123",
            role="RENTER",
        )

    @pytest.fixture
    def apartment(self, user_lessor):
        from apps.listings.models import Address, Apartment

        address = Address.objects.create(
            land="Bayern", city="München", street="Test 1", postal_code="80331"
        )
        return Apartment.objects.create(
            owner=user_lessor,
            address=address,
            title="Test Apt",
            description="Просторная светлая студия с современным ремонтом, кухней, ванной и балконом. Полностью меблирована, Wi-Fi, стиральная машина.",
            price=1000,
            rooms=2,
            housing_type="STUDIO",
            is_active=True,
        )

    def test_user_service_register(self):
        service = UserService()
        user = service.register(
            name="New User",
            email="new@test.com",
            password="StrongPass123!",
            role="RENTER",
        )
        assert user.email == "new@test.com"
        assert user.role == "RENTER"

    def test_user_service_duplicate_email(self):
        service = UserService()
        service.register("Test", "dup@test.com", "Pass123!", "RENTER")
        with pytest.raises(Exception):
            service.register("Dup", "dup@test.com", "Pass123!", "RENTER")

    def test_apartment_service_create(self, user_lessor):
        service = ApartmentService()
        data = {
            "title": "New Listing",
            "description": "Просторная светлая студия с современным ремонтом, кухней, ванной и балконом. Полностью меблирована.",
            "price": 1200,
            "rooms": 2,
            "housing_type": "STUDIO",
            "address": {
                "land": "Test",
                "city": "City",
                "street": "Str",
                "postal_code": "12345",
            },
        }
        apartment = service.create_listing(user_lessor, data)
        assert apartment.title == "New Listing"
        assert apartment.owner == user_lessor

    def test_reservation_service_overlapping_dates(self, apartment, user_renter):
        service = ReservationService()
        start = timezone.now().date() + timedelta(days=10)
        end = start + timedelta(days=5)

        service.create_reservation(
            user_renter,
            {
                "listing": apartment,
                "start_date": start,
                "end_date": end,
            },
        )

        with pytest.raises(Exception):
            service.create_reservation(
                user_renter,
                {
                    "listing": apartment,
                    "start_date": start + timedelta(days=3),
                    "end_date": end + timedelta(days=3),
                },
            )

    def test_reservation_service_past_dates(self, apartment, user_renter):
        service = ReservationService()
        with pytest.raises(Exception):
            service.create_reservation(
                user_renter,
                {
                    "listing": apartment,
                    "start_date": timezone.now().date() - timedelta(days=1),
                    "end_date": timezone.now().date() + timedelta(days=1),
                },
            )

    def test_review_service_only_after_checkin(self, apartment, user_renter):
        service = ReviewService()

        with pytest.raises(Exception):
            service.create_review(
                user_renter,
                {
                    "reservation": 999,
                    "rating": 5,
                    "comment": "Test",
                },
            )
