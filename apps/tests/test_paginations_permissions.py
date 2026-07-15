import pytest
from rest_framework.test import APIClient

from apps.common.permissions import IsLessor, IsRenter
from apps.listings.paginations.paginator import Paginator


@pytest.mark.django_db
class TestPaginationsAndPermissions:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user_lessor(self):
        from apps.users.models import User

        return User.objects.create_user(
            name="Lessor",
            email="lessor@test.com",
            password="StrongPass123!",
            role="LESSOR",
        )

    @pytest.fixture
    def user_renter(self):
        from apps.users.models import User

        return User.objects.create_user(
            name="Renter",
            email="renter@test.com",
            password="StrongPass123!",
            role="RENTER",
        )

    @pytest.fixture
    def apartments(self, user_lessor):
        from apps.listings.models import Address, Apartment

        addr = Address.objects.create(
            land="Bayern", city="München", street="Test", postal_code="80331"
        )
        for i in range(12):
            Apartment.objects.create(
                owner=user_lessor,
                address=addr,
                title=f"Apartment {i}",
                description="Хорошее описание для прохождения валидации.",
                price=1000 + i * 50,
                rooms=1 + (i % 3),
                housing_type="STUDIO",
                is_active=True,
            )
        return Apartment.objects.all()

    def test_listing_pagination(self, apartments):
        paginator = Paginator()
        result = paginator.paginate(apartments, page=1, page_size=5)

        assert len(result["items"]) == 5
        assert result["page"] == 1
        assert result["page_size"] == 5
        assert result["total"] == 12

    def test_listing_pagination_max_size(self, apartments):
        paginator = Paginator()
        result = paginator.paginate(apartments, page=1, page_size=100)
        assert result["page_size"] <= 50

    def test_is_lessor_permission(self, client, user_lessor):
        permission = IsLessor()
        request = client.request()
        request.user = user_lessor
        assert permission.has_permission(request, None) is True

    def test_is_renter_permission(self, client, user_renter):
        permission = IsRenter()
        request = client.request()
        request.user = user_renter
        assert permission.has_permission(request, None) is True

    def test_anonymous_user_permission_denied(self, client):
        permission = IsLessor()
        request = client.request()
        request.user = None
        assert permission.has_permission(request, None) is False

    def test_lessor_can_create_listing(self, client, user_lessor):
        client.force_authenticate(user=user_lessor)
        pass
