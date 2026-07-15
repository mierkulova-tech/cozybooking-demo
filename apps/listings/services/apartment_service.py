from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Count

from apps.common.utils.content import check_content_helper
from apps.listings.errors.listings_errors import (
    ListingNotFoundError,
    NotListingOwnerError,
)
from apps.listings.filters.listing_filter import ListingFilter
from apps.listings.paginations.paginator import Paginator
from apps.listings.repositories.apartment_repository import ApartmentRepository

if TYPE_CHECKING:
    from apps.listings.models import Apartment


class ApartmentService:
    def __init__(self):
        self.repository = ApartmentRepository()
        self.filter = ListingFilter()
        self.paginator = Paginator()

    POPULAR_SEARCHES_LIMIT = 10

    def list_listings(self, params: dict, user=None) -> dict:
        search = params.get("search")
        page = params.get("page") or 1

        if search and page == 1:
            self.repository.add_search(search, user)

        queryset = self.repository.active_queryset()

        queryset = self.filter.apply(queryset, params)

        return self.paginator.paginate(
            queryset,
            page=params.get("page"),
            page_size=params.get("page_size"),
        )

    def popular_searches(self) -> list:
        return list(
            Apartment.objects.filter(is_active=True)
            .annotate(views_count=Count("views", distinct=True))
            .order_by("-views_count")[: self.POPULAR_SEARCHES_LIMIT]
        )

    def get_listing(self, apartment_id: int, user) -> "Apartment":
        apartment = self.repository.get_active_by_id(apartment_id)

        if apartment is None:
            raise ListingNotFoundError()

        self.repository.add_view(apartment, user)

        return apartment

    def list_my_listings(self, owner) -> list:
        return list(self.repository.list_by_owner(owner.id))

    @transaction.atomic
    def create_listing(self, owner, validated_data: dict) -> "Apartment":
        address_data = validated_data.pop("address")

        address = self.repository.create_address(**address_data)

        return self.repository.create_apartment(
            owner=owner, address=address, **validated_data
        )

    @transaction.atomic
    def update_listing(
        self, user, apartment_id: int, validated_data: dict
    ) -> "Apartment":
        apartment = self._get_owned(user, apartment_id)

        address_data = validated_data.pop("address", None)

        if address_data:
            for field, value in address_data.items():
                setattr(apartment.address, field, value)

            apartment.address.save()

        for field, value in validated_data.items():
            setattr(apartment, field, value)

        return self.repository.save(apartment)

    def delete_listing(self, user, apartment_id: int) -> None:
        apartment = self._get_owned(user, apartment_id)

        self.repository.delete(apartment)

    def toggle_availability(self, user, apartment_id: int) -> "Apartment":
        apartment = self._get_owned(user, apartment_id)

        apartment.is_active = not apartment.is_active

        return self.repository.save(apartment)

    def _get_owned(self, user, apartment_id: int) -> "Apartment":
        apartment = self.repository.get_by_id(apartment_id)

        check_content_helper(apartment)

        if apartment.owner_id != user.id:
            raise NotListingOwnerError()

        return apartment
