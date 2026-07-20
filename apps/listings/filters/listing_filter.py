"""Filtering and sorting service class for apartment listings.

This module provides the ListingFilter class to apply search queries,
address filters, price/room boundaries, housing types, and sorting rules
onto a Django QuerySet.
"""

from django.db.models import Count, Q, QuerySet

from apps.listings.constants.filter_constants import (
    HOUSING_TYPE,
    LOCATION,
    ORDER,
    POPULAR,
    PRICE_MAX,
    PRICE_MIN,
    ROOMS_MAX,
    ROOMS_MIN,
    SEARCH,
)


class ListingFilter:
    """Class responsible for filtering and sorting apartment listing querysets.

    Filters and sorts querysets based on request parameters.
    """

    def apply(self, queryset: QuerySet, params: dict) -> QuerySet:
        """Apply filters and sorting rules to the given queryset.

        Args:
            queryset (QuerySet): The initial apartment queryset.
            params (dict): Dictionary of query parameters.

        Returns:
            QuerySet: The filtered and sorted queryset.
        """
        queryset = self._filter(queryset, params)

        queryset = self._sort(queryset, params.get(ORDER))

        return queryset

    def _filter(self, queryset: QuerySet, params: dict) -> QuerySet:
        """Filter the queryset by search query, location, price, rooms, and housing type.

        Args:
            queryset (QuerySet): The queryset to filter.
            params (dict): Dictionary of filtering parameters.

        Returns:
            QuerySet: The filtered queryset.
        """
        search = params.get(SEARCH)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        location = params.get(LOCATION)
        if location:
            queryset = queryset.filter(
                Q(address__city__icontains=location) | Q(address__land__icontains=location)
            )

        price_min = params.get(PRICE_MIN)
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)

        price_max = params.get(PRICE_MAX)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)

        rooms_min = params.get(ROOMS_MIN)
        if rooms_min is not None:
            queryset = queryset.filter(rooms__gte=rooms_min)

        rooms_max = params.get(ROOMS_MAX)
        if rooms_max is not None:
            queryset = queryset.filter(rooms__lte=rooms_max)

        housing_type = params.get(HOUSING_TYPE)
        if housing_type:
            queryset = queryset.filter(housing_type=housing_type)

        return queryset

    def _sort(self, queryset: QuerySet, order: str | None) -> QuerySet:
        """Sort the queryset by the specified field, including custom handling for popularity.

        Args:
            queryset (QuerySet): The queryset to sort.
            order (str | None): The ordering field string.

        Returns:
            QuerySet: The sorted queryset.
        """
        if not order:
            return queryset

        if order.lstrip("-") == POPULAR:
            direction = "-views_count" if order.startswith("-") else "views_count"

            return queryset.annotate(views_count=Count("views", distinct=True)).order_by(direction)

        return queryset.order_by(order)
