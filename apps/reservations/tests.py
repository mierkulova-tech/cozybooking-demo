from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.reservations.choices.status_choices import StatusChoices


class CozyBookingFlowTests(APITestCase):
    def setUp(self):
        self.today = timezone.now().date()

        cache.clear()

    def _register(self, email, role, name="Тест"):
        return self.client.post(
            reverse("users:register"),
            {
                "name": name,
                "email": email,
                "password": "StrongPass123",
                "role": role,
            },
            format="json",
        )

    def _login(self, email):
        resp = self.client.post(
            reverse("users:login"),
            {
                "email": email,
                "password": "StrongPass123",
            },
            format="json",
        )
        return resp.data["access"]

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _logout_client(self):
        self.client.credentials()

    def _create_listing(self, token):
        self._auth(token)
        resp = self.client.post(
            reverse("listings:list"),
            {
                "title": "Уютная студия в центре",
                "description": "Светлая студия рядом с метро",
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
        self.assertEqual(
            self._register("lessor@test.de", "LESSOR").status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            self._register("renter@test.de", "RENTER").status_code,
            status.HTTP_201_CREATED,
        )

        lessor_token = self._login("lessor@test.de")
        renter_token = self._login("renter@test.de")

        listing_resp = self._create_listing(lessor_token)
        self.assertEqual(listing_resp.status_code, status.HTTP_201_CREATED)
        listing_id = listing_resp.data["id"]

        self._logout_client()
        catalog = self.client.get(reverse("listings:list"))
        self.assertEqual(catalog.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(catalog.data["total"], 1)

        self._auth(renter_token)
        start = self.today + timedelta(days=10)
        end = self.today + timedelta(days=15)
        booking = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
            format="json",
        )
        self.assertEqual(booking.status_code, status.HTTP_201_CREATED)
        self.assertEqual(booking.data["status"], StatusChoices.PENDING)
        reservation_id = booking.data["id"]

        self._auth(lessor_token)
        confirm = self.client.patch(
            reverse("reservations:status", args=[reservation_id]),
            {"status": StatusChoices.CONFIRMED},
            format="json",
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)

        checkin = self.client.patch(
            reverse("reservations:status", args=[reservation_id]),
            {"status": StatusChoices.CHECKED_IN},
            format="json",
        )
        self.assertEqual(checkin.status_code, status.HTTP_200_OK)

        self._auth(renter_token)
        review = self.client.post(
            reverse("reviews:create"),
            {
                "reservation": reservation_id,
                "rating": 5,
                "comment": "Всё отлично!",
            },
            format="json",
        )
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)

        self._logout_client()
        reviews = self.client.get(reverse("reviews:by-listing", args=[listing_id]))
        self.assertEqual(reviews.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reviews.data), 1)

    def test_renter_cannot_create_listing(self):
        self._register("r2@test.de", "RENTER")
        self._auth(self._login("r2@test.de"))
        resp = self.client.post(reverse("listings:list"), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

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
            reverse("reservations:create"),
            {"listing": listing_id, "start_date": start, "end_date": end},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=22)).isoformat(),
                "end_date": (self.today + timedelta(days=27)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_in_past(self):
        self._register("l4@test.de", "LESSOR")
        self._register("r4@test.de", "RENTER")
        listing_id = self._create_listing(self._login("l4@test.de")).data["id"]
        self._auth(self._login("r4@test.de"))
        resp = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": (self.today - timedelta(days=2)).isoformat(),
                "end_date": (self.today + timedelta(days=2)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_requires_checked_in(self):
        self._register("l5@test.de", "LESSOR")
        self._register("r5@test.de", "RENTER")
        lessor_token = self._login("l5@test.de")
        renter_token = self._login("r5@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(renter_token)
        booking = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=30)).isoformat(),
                "end_date": (self.today + timedelta(days=33)).isoformat(),
            },
            format="json",
        )
        reservation_id = booking.data["id"]

        resp = self.client.post(
            reverse("reviews:create"),
            {"reservation": reservation_id, "rating": 4, "comment": "рано"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_resurrect_canceled_reservation(self):
        """#1 стейт-машина: отменённую бронь нельзя вернуть в CONFIRMED."""
        self._register("l6@test.de", "LESSOR")
        self._register("r6@test.de", "RENTER")
        lessor_token = self._login("l6@test.de")
        renter_token = self._login("r6@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(renter_token)
        booking = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=40)).isoformat(),
                "end_date": (self.today + timedelta(days=45)).isoformat(),
            },
            format="json",
        )
        reservation_id = booking.data["id"]

        cancel = self.client.patch(
            reverse("reservations:status", args=[reservation_id]),
            {"status": StatusChoices.CANCELED},
            format="json",
        )
        self.assertEqual(cancel.status_code, status.HTTP_200_OK)

        self._auth(lessor_token)
        resurrect = self.client.patch(
            reverse("reservations:status", args=[reservation_id]),
            {"status": StatusChoices.CONFIRMED},
            format="json",
        )
        self.assertEqual(resurrect.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_inactive_listing(self):
        self._register("l7@test.de", "LESSOR")
        self._register("r7@test.de", "RENTER")
        lessor_token = self._login("l7@test.de")
        renter_token = self._login("r7@test.de")
        listing_id = self._create_listing(lessor_token).data["id"]

        self._auth(lessor_token)
        self.client.post(reverse("listings:availability", args=[listing_id]))

        self._auth(renter_token)
        resp = self.client.post(
            reverse("reservations:create"),
            {
                "listing": listing_id,
                "start_date": (self.today + timedelta(days=50)).isoformat(),
                "end_date": (self.today + timedelta(days=55)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_rejected(self):
        resp = self.client.post(
            reverse("users:register"),
            {
                "name": "Weak",
                "email": "weak@test.de",
                "password": "password",
                "role": "RENTER",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
