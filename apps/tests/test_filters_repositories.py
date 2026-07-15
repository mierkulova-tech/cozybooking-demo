from datetime import timedelta

import pytest
from django.utils import timezone

from apps.listings.filters.listing_filter import ListingFilter
from apps.listings.models import Apartment
from apps.listings.repositories.apartment_repository import ApartmentRepository
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.repositories.reservation_repository import ReservationRepository
from apps.reviews.repositories.review_repository import ReviewRepository


@pytest.mark.django_db
class TestFiltersAndRepositories:
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
    def apartments(self, user_lessor):
        from apps.listings.models import Address

        addr = Address.objects.create(
            land="Bayern", city="München", street="Test", postal_code="80331"
        )

        apts = []
        for i in range(5):
            apts.append(
                Apartment.objects.create(
                    owner=user_lessor,
                    address=addr,
                    title=f"Apartment {i}",
                    description="Test desc",
                    price=800 + i * 100,
                    rooms=1 + i % 3,
                    housing_type="STUDIO",
                    is_active=True,
                )
            )
        return apts

    def test_listing_filter_by_price(self, apartments):
        filter_service = ListingFilter()
        qs = filter_service.apply(
            queryset=Apartment.objects.all(),
            params={"price_min": 900, "price_max": 1100},
        )
        assert qs.count() == 3

    def test_listing_filter_by_rooms(self, apartments):
        filter_service = ListingFilter()
        qs = filter_service.apply(
            queryset=Apartment.objects.all(), params={"rooms_min": 2}
        )
        assert qs.count() >= 2

    def test_listing_filter_search(self, apartments):
        filter_service = ListingFilter()
        qs = filter_service.apply(
            queryset=Apartment.objects.all(), params={"search": "Apartment 3"}
        )
        assert qs.count() == 1

    def test_listing_order_by_price(self, apartments):
        filter_service = ListingFilter()
        qs = filter_service.apply(
            queryset=Apartment.objects.all(), params={"order": "price"}
        )
        prices = list(qs.values_list("price", flat=True))
        assert prices == sorted(prices)

    def test_apartment_repository_list_my(self, user_lessor, apartments):
        repo = ApartmentRepository()
        my_listings = repo.list_by_owner(user_lessor.id)
        assert my_listings.count() == 5

    def test_reservation_repository_get_by_id(self, apartments, user_renter):
        from apps.reservations.models import Reservation

        reservation = Reservation.objects.create(
            listing=apartments[0],
            user=user_renter,
            start_date=timezone.now().date() + timedelta(days=5),
            end_date=timezone.now().date() + timedelta(days=10),
            status=StatusChoices.PENDING,
            price=5000,
        )
        repo = ReservationRepository()
        found = repo.get_by_id(reservation.id)
        assert found is not None
        assert found.id == reservation.id

    def test_review_repository_exists_for_reservation(
        self, apartment, user_renter, reservation
    ):
        repo = ReviewRepository()
        assert not repo.exists_for_reservation(reservation.id)

        from apps.reviews.models import Review

        Review.objects.create(
            listing=apartment,
            user=user_renter,
            reservation=reservation,
            rating=5,
            comment="Good",
        )
        assert repo.exists_for_reservation(reservation.id)

    def test_review_repository_list_by_listing(
        self, apartment, user_renter, reservation
    ):
        from apps.reviews.models import Review

        Review.objects.create(
            listing=apartment,
            user=user_renter,
            reservation=reservation,
            rating=5,
            comment="Test",
        )
        repo = ReviewRepository()
        reviews = repo.list_by_listing(apartment.id)
        assert reviews.count() == 1
