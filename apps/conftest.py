"""Pytest fixtures and configuration settings for testing the cozybooking project.

This module provides common test fixtures including API clients, test users with
different roles (renter/lessor), mock addresses, apartments, reservations,
and parameterized test hooks (`pytest_generate_tests`).
"""

import os
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.reservations.choices.status_choices import StatusChoices

# Disable forced HTTPS redirect for testing environments
os.environ["SECURE_SSL_REDIRECT"] = "False"


@pytest.fixture
def api_client():
    """Provide an instance of Django REST Framework's APIClient for testing requests."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user_renter(db):
    """Create and return a test user with the RENTER role."""
    from apps.users.models import User

    return User.objects.create_user(
        name="Test Renter",
        email="renter@test.com",
        password="StrongPass123!",
        role="RENTER",
    )


@pytest.fixture
def user_lessor(db):
    """Create and return a test user with the LESSOR role."""
    from apps.users.models import User

    return User.objects.create_user(
        name="Test Lessor",
        email="lessor@test.com",
        password="StrongPass123!",
        role="LESSOR",
    )


@pytest.fixture
def address(db):
    """Create and return a sample Address instance for listings."""
    from apps.listings.models import Address

    return Address.objects.create(
        land="Bayern", city="München", street="Marienplatz 1", postal_code="80331"
    )


@pytest.fixture
def apartment(db, user_lessor, address):
    """Create and return a sample Apartment listing owned by the test lessor."""
    from apps.listings.models import Apartment

    return Apartment.objects.create(
        owner=user_lessor,
        address=address,
        title="Cozy studio in the center of Munich",
        description="Spacious and bright studio with modern renovation,"
        "kitchen, bathroom, and balcony. Fully furnished, Wi-Fi,"
        "washing machine. Ideal for long-term living.",
        price=1250,
        rooms=2,
        housing_type="STUDIO",
        is_active=True,
    )


@pytest.fixture
def reservation(db, apartment, user_renter):
    """Create and return a pending reservation for an apartment by a renter."""
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
    """Update a reservation status to CHECKED_IN and return it."""
    reservation.status = StatusChoices.CHECKED_IN
    reservation.save()
    return reservation


def pytest_generate_tests(metafunc):
    """Dynamically parameterize tests based on available fixture names."""
    if "filter_params" in metafunc.fixturenames:
        metafunc.parametrize(
            "filter_params",
            [
                ({"price_min": 900, "price_max": 1400}, 5),
                ({"rooms_min": 2}, 4),
                ({"search": "studio"}, 3),
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
