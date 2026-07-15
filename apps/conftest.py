import os
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.reservations.choices.status_choices import StatusChoices

os.environ["SECURE_SSL_REDIRECT"] = "False"


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user_renter(db):
    from apps.users.models import User

    return User.objects.create_user(
        name="Test Renter",
        email="renter@test.com",
        password="StrongPass123!",
        role="RENTER",
    )


@pytest.fixture
def user_lessor(db):
    from apps.users.models import User

    return User.objects.create_user(
        name="Test Lessor",
        email="lessor@test.com",
        password="StrongPass123!",
        role="LESSOR",
    )


@pytest.fixture
def address(db):
    from apps.listings.models import Address

    return Address.objects.create(
        land="Bayern", city="München", street="Marienplatz 1", postal_code="80331"
    )


@pytest.fixture
def apartment(db, user_lessor, address):
    from apps.listings.models import Apartment

    return Apartment.objects.create(
        owner=user_lessor,
        address=address,
        title="Уютная студия в центре Мюнхена",
        description="Просторная светлая студия с современным ремонтом, кухней, ванной и балконом. Полностью меблирована, Wi-Fi, стиральная машина. Идеально для длительного проживания.",
        price=1250,
        rooms=2,
        housing_type="STUDIO",
        is_active=True,
    )


@pytest.fixture
def reservation(db, apartment, user_renter):
    from apps.reservations.choices.status_choices import StatusChoices
    from apps.reservations.models import Reservation

    return Reservation.objects.create(
        listing=apartment,
        user=user_renter,
        start_date=timezone.now().date() + timedelta(days=10),
        end_date=timezone.now().date() + timedelta(days=15),
        status=StatusChoices.PENDING,
        price=1250 * 5,
    )


@pytest.fixture
def reservation_checked_in(db, reservation):
    reservation.status = StatusChoices.CHECKED_IN
    reservation.save()
    return reservation


def pytest_generate_tests(metafunc):
    if "filter_params" in metafunc.fixturenames:
        metafunc.parametrize(
            "filter_params",
            [
                ({"price_min": 900, "price_max": 1400}, 5),
                ({"rooms_min": 2}, 4),
                ({"search": "студия"}, 3),
                ({"housing_type": "STUDIO"}, 6),
                ({}, 10),
                ({"order": "price"}, None),
                ({"order": "-popular"}, None),
            ],
            ids=[
                "price_range",
                "rooms",
                "search",
                "housing_type",
                "no_filter",
                "sort_price",
                "sort_popular",
            ],
        )

    if "reservation_status" in metafunc.fixturenames:
        metafunc.parametrize(
            "reservation_status",
            [
                (StatusChoices.PENDING, True),
                (StatusChoices.CONFIRMED, True),
                (StatusChoices.CHECKED_IN, True),
                (StatusChoices.CANCELED, False),
                (StatusChoices.REJECTED, False),
            ],
            ids=["pending", "confirmed", "checked_in", "canceled", "rejected"],
        )

    if "role_test" in metafunc.fixturenames:
        metafunc.parametrize(
            "role_test",
            [
                ("LESSOR", True, 201),
                ("RENTER", False, 403),
                ("LESSOR", True, 200),
            ],
            ids=["lessor_create", "renter_create", "lessor_edit"],
        )
