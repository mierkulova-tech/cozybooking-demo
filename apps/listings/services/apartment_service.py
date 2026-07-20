"""Business logic for browsing, creating, and managing apartment listings."""

from django.db import transaction

from apps.common.utils.content import check_content_helper
from apps.listings.errors.listings_errors import (
    ListingNotFoundError,
    NotListingOwnerError,
)
from apps.listings.filters.listing_filter import ListingFilter
from apps.listings.models import Apartment
from apps.listings.paginations.paginator import Paginator
from apps.listings.repositories.apartment_repository import ApartmentRepository


class ApartmentService:
    """Coordinates listing search, CRUD, visibility toggling, and search stats."""

    def __init__(self):
        """Initialize the apartment service with repository and filter dependencies."""
        self.repository = ApartmentRepository()
        self.filter = ListingFilter()
        self.paginator = Paginator()

    POPULAR_SEARCHES_LIMIT = 10

    def list_listings(self, params: dict, user=None) -> dict:
        """Return a filtered, paginated list of active listings.

        Also records the search keyword (on the first page only) for the
        popular-searches feature.

        Args:
            params: Validated query parameters (search, filters, page, page_size).
            user: The requesting user, or None for anonymous visitors.

        Returns:
            A dict with "items", "page", "page_size", and "total".
        """
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
        """Return the most frequent search keywords, up to POPULAR_SEARCHES_LIMIT."""
        return self.repository.popular_searches(self.POPULAR_SEARCHES_LIMIT)

    def popular_listings(self) -> list:
        """Return the most-viewed active listings, up to POPULAR_SEARCHES_LIMIT."""
        return self.repository.most_viewed_active(self.POPULAR_SEARCHES_LIMIT)

    def get_listing(self, apartment_id: int, user) -> "Apartment":
        """Fetch an active listing by ID and record a view for it.

        Args:
            apartment_id: The ID of the listing to fetch.
            user: The requesting user (or anonymous), recorded as the viewer.

        Returns:
            The Apartment instance.

        Raises:
            ListingNotFoundError: If no active listing exists with this ID.
        """
        apartment = self.repository.get_active_by_id(apartment_id)

        if apartment is None:
            raise ListingNotFoundError()

        self.repository.add_view(apartment, user)

        return apartment

    def list_my_listings(self, owner) -> list:
        """Return all listings (active and hidden) owned by the given user."""
        return list(self.repository.list_by_owner(owner.id))

    @transaction.atomic
    def create_listing(self, owner, validated_data: dict) -> "Apartment":
        """Create a new address and apartment listing for the given owner.

        Args:
            owner: The lessor who will own the listing.
            validated_data: Validated listing data, including a nested "address".

        Returns:
            The newly created Apartment instance.
        """
        address_data = validated_data.pop("address")

        address = self.repository.create_address(**address_data)

        return self.repository.create_apartment(owner=owner, address=address, **validated_data)

    @transaction.atomic
    def update_listing(self, user, apartment_id: int, validated_data: dict) -> "Apartment":
        """Update a listing (and optionally its address), enforcing ownership.

        Args:
            user: The user requesting the update.
            apartment_id: The ID of the listing to update.
            validated_data: Validated fields to update, optionally including
                a nested "address" dict.

        Returns:
            The updated Apartment instance.

        Raises:
            NotListingOwnerError: If the user does not own the listing.
        """
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
        """Delete a listing, enforcing ownership.

        Args:
            user: The user requesting deletion.
            apartment_id: The ID of the listing to delete.

        Raises:
            NotListingOwnerError: If the user does not own the listing.
        """
        apartment = self._get_owned(user, apartment_id)

        self.repository.delete(apartment)

    def toggle_availability(self, user, apartment_id: int) -> "Apartment":
        """Flip a listing's `is_active` flag, enforcing ownership.

        Args:
            user: The user requesting the change.
            apartment_id: The ID of the listing to toggle.

        Returns:
            The updated Apartment instance.

        Raises:
            NotListingOwnerError: If the user does not own the listing.
        """
        apartment = self._get_owned(user, apartment_id)

        apartment.is_active = not apartment.is_active

        return self.repository.save(apartment)

    def _get_owned(self, user, apartment_id: int) -> "Apartment":
        """Fetch a listing by ID and verify the given user owns it.

        Args:
            user: The user expected to own the listing.
            apartment_id: The ID of the listing to fetch.

        Returns:
            The Apartment instance.

        Raises:
            NoContentError: If no listing exists with this ID.
            NotListingOwnerError: If the user does not own the listing.
        """
        apartment = self.repository.get_by_id(apartment_id)

        check_content_helper(apartment)

        if apartment.owner_id != user.id:
            raise NotListingOwnerError()

        return apartment
