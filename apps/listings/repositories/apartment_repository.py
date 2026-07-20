"""Database repository module for apartment listings, addresses, and history logs.

This module encapsulates data access logic for apartments, addresses,
as well as view and search history tracking.
"""

from django.db.models import Count, QuerySet

from apps.listings.models import Address, Apartment, SearchHistory, ViewHistory


class ApartmentRepository:
    """Repository class handling database queries and persistence.

    Manages apartment listings and related entities.
    """

    def active_queryset(self) -> QuerySet:
        """Retrieve a queryset of all active apartments with optimized related fields.

        Returns:
            QuerySet: QuerySet of active Apartment instances.
        """
        return Apartment.objects.select_related("address", "owner").filter(is_active=True)

    def get_active_by_id(self, apartment_id: int) -> Apartment | None:
        """Retrieve a single active apartment by its ID.

        Args:
            apartment_id (int): The unique identifier of the apartment.

        Returns:
            Apartment | None: The apartment instance if found and active, else None.
        """
        return (
            Apartment.objects.select_related("address", "owner")
            .filter(id=apartment_id, is_active=True)
            .first()
        )

    def get_by_id(self, apartment_id: int) -> Apartment | None:
        """Retrieve any apartment (active or inactive) by its ID.

        Args:
            apartment_id (int): The unique identifier of the apartment.

        Returns:
            Apartment | None: The apartment instance if found, else None.
        """
        return Apartment.objects.select_related("address", "owner").filter(id=apartment_id).first()

    def list_by_owner(self, owner_id: int) -> QuerySet:
        """Retrieve all apartment listings owned by a specific user.

        Args:
            owner_id (int): The unique identifier of the owner.

        Returns:
            QuerySet: QuerySet of apartments belonging to the owner,
            ordered by creation date descending.
        """
        return (
            Apartment.objects.select_related("address", "owner")
            .filter(owner_id=owner_id)
            .order_by("-created_at")
        )

    def create_address(self, **data) -> Address:
        """Create and persist a new Address instance.

        Args:
            **data: Keyword arguments representing address fields.

        Returns:
            Address: The created Address instance.
        """
        return Address.objects.create(**data)

    def create_apartment(self, owner, address: Address, **data) -> Apartment:
        """Create and persist a new Apartment instance linked to an owner and address.

        Args:
            owner: The user owning the apartment.
            address (Address): The address associated with the apartment.
            **data: Additional apartment attribute keyword arguments.

        Returns:
            Apartment: The created Apartment instance.
        """
        return Apartment.objects.create(owner=owner, address=address, **data)

    def save(self, apartment: Apartment) -> Apartment:
        """Save changes to an existing apartment instance.

        Args:
            apartment (Apartment): The apartment instance to save.

        Returns:
            Apartment: The saved apartment instance.
        """
        apartment.save()
        return apartment

    def delete(self, apartment: Apartment) -> None:
        """Delete an apartment instance from the database.

        Args:
            apartment (Apartment): The apartment instance to delete.
        """
        apartment.delete()

    def deactivate_by_owner(self, owner_id: int) -> int:
        """Deactivate all active apartments belonging to a specific owner.

        Args:
            owner_id (int): The unique identifier of the owner.

        Returns:
            int: The number of updated apartment rows.
        """
        return Apartment.objects.filter(owner_id=owner_id, is_active=True).update(is_active=False)

    def add_view(self, apartment: Apartment, user) -> None:
        """Record a view history entry for an apartment by a user (or anonymous).

        Args:
            apartment (Apartment): The apartment being viewed.
            user: The user viewing the apartment, or None/unauthenticated.
        """
        ViewHistory.objects.create(
            apartment=apartment,
            user=user if user and user.is_authenticated else None,
        )

    def add_search(self, keyword: str, user) -> None:
        """Record a search query keyword history entry.

        Args:
            keyword (str): The search keyword entered.
            user: The user performing the search, or None/unauthenticated.
        """
        SearchHistory.objects.create(
            keyword=keyword,
            user=user if user and user.is_authenticated else None,
        )

    def popular_searches(self, limit: int) -> list[dict]:
        """Retrieve the most frequent search keywords annotated with counts.

        Args:
            limit (int): The maximum number of popular searches to return.

        Returns:
            list[dict]: A list of dictionaries containing keywords and their counts.
        """
        return list(
            SearchHistory.objects.values("keyword")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
