"""Constants for search, filtering, and pagination parameters.

This module defines query parameter constants and configuration limits
for filtering, ordering, and paginating listings.
"""

SEARCH = "search"

LOCATION = "location"

PRICE_MIN = "price_min"

PRICE_MAX = "price_max"

ROOMS_MIN = "rooms_min"

ROOMS_MAX = "rooms_max"

HOUSING_TYPE = "housing_type"

ORDER = "order"

PAGE = "page"

PAGE_SIZE = "page_size"

DEFAULT_PAGE_SIZE = 10

MAX_PAGE_SIZE = 50

POPULAR = "popular"

ALLOWED_ORDER_FIELDS = {
    "price",
    "-price",
    "created_at",
    "-created_at",
    POPULAR,
    f"-{POPULAR}",
}
