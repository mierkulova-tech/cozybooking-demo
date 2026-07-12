
from django.db.models import Count, QuerySet

from apps.listings.models import Address, Apartment, SearchHistory, ViewHistory


class ApartmentRepository:

    def active_queryset(self) -> QuerySet:

        return Apartment.objects.select_related("address", "owner").filter(
            is_active=True
        )

    def get_active_by_id(self, apartment_id: int) -> Apartment | None:

        return (
            Apartment.objects.select_related("address", "owner")
            .filter(id=apartment_id, is_active=True)
            .first()
        )

    def get_by_id(self, apartment_id: int) -> Apartment | None:

        return (
            Apartment.objects.select_related("address", "owner")
            .filter(id=apartment_id)
            .first()
        )

    def list_by_owner(self, owner_id: int) -> QuerySet:

        return (
            Apartment.objects.select_related("address", "owner")
            .filter(owner_id=owner_id)
            .order_by("-created_at")
        )

    def create_address(self, **data) -> Address:
        return Address.objects.create(**data)

    def create_apartment(self, owner, address: Address, **data) -> Apartment:
        return Apartment.objects.create(owner=owner, address=address, **data)

    def save(self, apartment: Apartment) -> Apartment:
        apartment.save()
        return apartment

    def delete(self, apartment: Apartment) -> None:
        apartment.delete()

    def add_view(self, apartment: Apartment, user) -> None:

        ViewHistory.objects.create(
            apartment=apartment,
            user=user if user and user.is_authenticated else None,
        )

    def add_search(self, keyword: str, user) -> None:

        SearchHistory.objects.create(
            keyword=keyword,
            user=user if user and user.is_authenticated else None,
        )

    def popular_searches(self, limit: int) -> list[dict]:

        return list(
            SearchHistory.objects.values("keyword")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
