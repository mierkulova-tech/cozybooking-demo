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
    def apply(self, queryset: QuerySet, params: dict) -> QuerySet:
        queryset = self._filter(queryset, params)
        queryset = self._sort(queryset, params.get(ORDER))
        return queryset

    # --- Поиск и фильтрация -------------------------------------------------
    def _filter(self, queryset: QuerySet, params: dict) -> QuerySet:
        search = params.get(SEARCH)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        location = params.get(LOCATION)
        if location:
            queryset = queryset.filter(
                Q(address__city__icontains=location)
                | Q(address__land__icontains=location)
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
        if not order:
            return queryset

        if order.lstrip("-") == POPULAR:
            direction = "-views_count" if order.startswith("-") else "views_count"
            return queryset.annotate(
                views_count=Count("views__user", distinct=True)
            ).order_by(direction)

        return queryset.order_by(order)
