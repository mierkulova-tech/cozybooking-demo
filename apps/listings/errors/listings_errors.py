from apps.common.exceptions.base import (
    ApplicationError,
    NoContentError,
    PermissionDeniedError,
)


class ListingNotFoundError(NoContentError):
    default_detail = "Объявление не найдено."
    default_code = "listing_not_found"


class NotListingOwnerError(PermissionDeniedError):
    default_detail = "Можно управлять только своими объявлениями."
    default_code = "not_listing_owner"


class PageParameterError(ApplicationError):
    default_detail = "Некорректный параметр пагинации."
    default_code = "invalid_page_parameter"
