from django.db.models import QuerySet

from apps.listings.constants.filter_constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from apps.listings.errors.listings_errors import PageParameterError


class Paginator:
    def paginate(
        self, queryset: QuerySet, page: int | None, page_size: int | None
    ) -> dict:
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
