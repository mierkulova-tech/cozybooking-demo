"""Pagination utility class for apartment listing querysets.

This module provides the Paginator class to slice querysets based on page
numbers and page sizes while enforcing maximum page size limits and offsets.
"""

from django.db.models import QuerySet

from apps.listings.constants.filter_constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from apps.listings.errors.listings_errors import PageParameterError


class Paginator:
    """Class responsible for paginating Django QuerySets for listing endpoints."""

    def paginate(self, queryset: QuerySet, page: int | None, page_size: int | None) -> dict:
        """Slice and paginate a given queryset based on the requested page and page size.

        Args:
            queryset (QuerySet): The queryset to paginate.
            page (int | None): The target page number.
            page_size (int | None): The number of items per page.

        Returns:
            dict: A dictionary containing paginated items, current page, page size, and total count.

        Raises:
            PageParameterError: If page or page_size is less than 1.
        """
        page = page or 1

        page_size = page_size or DEFAULT_PAGE_SIZE

        if page < 1:
            raise PageParameterError()

        if page_size < 1:
            raise PageParameterError()

        page_size = min(page_size, MAX_PAGE_SIZE)

        total = queryset.count()

        offset = (page - 1) * page_size

        items = queryset[offset : offset + page_size]

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
        }
