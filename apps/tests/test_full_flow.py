from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status

from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.models import Reservation


@pytest.mark.django_db
class TestCozyBookingFullFlow:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.today = timezone.now().date()
        cache.clear()

    def _register(self, email: str, role: str, name: str = "Тест"):
        return self.client.post(
            "/api/v1/users/register/",
            {
                "name": name,
                "email": email,
                "password": "StrongPass123!",
                "role": role,
            },
            format="json",
        )

    def _login(self, email: str):
        resp = self.client.post(
            "/api/v1/users/login/",
            {"email": email, "password": "StrongPass123!"},
            format="json",
        )
        return resp.data.get("access")

    def _auth(self, token: str):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _logout(self):
        self.client.credentials()

    def _create_listing(self, token: str):
        self._auth(token)
        resp = self.client.post(
            "/api/v1/listings/",
            {
                "title": "Уютная студия в центре",
                "description": "Светлая студия рядом с метро, все красиво и уютно, всем нравиться",
                "price": "850.00",
                "rooms": 1,
                "housing_type": "STUDIO",
                "address": {
                    "land": "Bayern",
                    "city": "München",
                    "street": "Marienplatz 1",
                    "postal_code": "80331",
                },
            },
            format="json",
        )
        return resp

    def test_full_happy_path(self):
        assert (
            self._register("lessor@test.de", "LESSOR").status_code
            == status.HTTP_201_CREATED
        )
        assert (
            self._register("renter@test.de", "RENTER").status_code
            == status.HTTP_201_CREATED
        )

        lessor_token = self._login("lessor@test.de")
        renter_token = self._login("renter@test.de")

        listing_resp = self._create_listing(lessor_token)
        assert listing_resp.status_code == status.HTTP_201_CREATED
        listing_id = listing_resp.data["id"]

        self._logout()
        catalog = self.client.get("/api/v1/listings/")
        assert catalog.status_code == status.HTTP_200_OK
        assert catalog.data.get("total", 0) >= 1

        self._auth(renter_token)
        start = self.today + timedelta(days=10)
        end = self.today + timedelta(days=15)
        booking = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
            format="json",
        )
        assert booking.status_code == status.HTTP_201_CREATED
        assert booking.data["status"] == StatusChoices.PENDING
        reservation_id = booking.data["id"]

        self._auth(lessor_token)
        confirm = self.client.patch(
            f"/api/v1/reservations/{reservation_id}/confirm/",
            format="json",
        )
        assert confirm.status_code == status.HTTP_200_OK

        Reservation.objects.filter(pk=reservation_id).update(
            start_date=self.today,
            end_date=self.today + timedelta(days=5),
        )

        checkin = self.client.patch(
            f"/api/v1/reservations/{reservation_id}/check-in/",
            format="json",
        )
        assert checkin.status_code == status.HTTP_200_OK

        self._auth(renter_token)
        review = self.client.post(
            "/api/v1/reviews/",
            {
                "reservation": reservation_id,
                "rating": 5,
                "comment": "Всё отлично!",
            },
            format="json",
        )
        assert review.status_code == status.HTTP_201_CREATED

        self._logout()
        reviews = self.client.get(f"/api/v1/reviews/listing/{listing_id}/")
        assert reviews.status_code == status.HTTP_200_OK
        assert len(reviews.data) == 1

    def test_renter_cannot_create_listing(self):
        self._register("r2@test.de", "RENTER")
        self._auth(self._login("r2@test.de"))
        resp = self.client.post("/api/v1/listings/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_overlapping_booking_rejected(self):
        self._register("l3@test.de", "LESSOR")
        self._register("r3@test.de", "RENTER")
        lessor_token = self._login("l3@test.de")
        renter_token = self._login("r3@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(renter_token)
        start = (self.today + timedelta(days=20)).isoformat()
        end = (self.today + timedelta(days=25)).isoformat()
        first = self.client.post(
            "/api/v1/reservations/",
            {"listing": listing_id, "start_date": start, "end_date": end},
            format="json",
        )
        assert first.status_code == status.HTTP_201_CREATED

        second = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=22)).isoformat(),
                "end_date": (self.today + timedelta(days=27)).isoformat(),
            },
            format="json",
        )
        assert second.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_book_in_past(self):
        self._register("l4@test.de", "LESSOR")
        self._register("r4@test.de", "RENTER")
        listing_id = self._create_listing(self._login("l4@test.de")).data["id"]

        self._auth(self._login("r4@test.de"))
        resp = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": (self.today - timedelta(days=2)).isoformat(),
                "end_date": (self.today + timedelta(days=2)).isoformat(),
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_review_requires_checked_in(self):
        self._register("l5@test.de", "LESSOR")
        self._register("r5@test.de", "RENTER")
        lessor_token = self._login("l5@test.de")
        renter_token = self._login("r5@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(renter_token)
        booking = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=30)).isoformat(),
                "end_date": (self.today + timedelta(days=33)).isoformat(),
            },
            format="json",
        )
        reservation_id = booking.data["id"]

        resp = self.client.post(
            "/api/v1/reviews/",
            {"reservation": reservation_id, "rating": 4, "comment": "рано"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_resurrect_canceled_reservation(self):
        self._register("l6@test.de", "LESSOR")
        self._register("r6@test.de", "RENTER")
        lessor_token = self._login("l6@test.de")
        renter_token = self._login("r6@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(renter_token)
        booking = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=40)).isoformat(),
                "end_date": (self.today + timedelta(days=45)).isoformat(),
            },
            format="json",
        )
        reservation_id = booking.data["id"]

        self._auth(renter_token)
        cancel = self.client.patch(
            f"/api/v1/reservations/{reservation_id}/cancel/",
            {"status": StatusChoices.CANCELED},
            format="json",
        )
        assert cancel.status_code == status.HTTP_200_OK

        self._auth(lessor_token)
        resurrect = self.client.patch(
            f"/api/v1/reservations/{reservation_id}/confirm/",
            {"status": StatusChoices.CONFIRMED},
            format="json",
        )
        assert resurrect.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_book_inactive_listing(self):
        self._register("l7@test.de", "LESSOR")
        self._register("r7@test.de", "RENTER")
        lessor_token = self._login("l7@test.de")
        renter_token = self._login("r7@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(lessor_token)
        toggle_resp = self.client.post(f"/api/v1/listings/{listing_id}/availability/")
        assert toggle_resp.status_code == 200

        self._auth(renter_token)
        resp = self.client.post(
            "/api/v1/reservations/",
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=50)).isoformat(),
                "end_date": (self.today + timedelta(days=55)).isoformat(),
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_rejected(self):
        resp = self.client.post(
            "/api/v1/users/register/",
            {
                "name": "Weak",
                "email": "weak@test.de",
                "password": "password",
                "role": "RENTER",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
