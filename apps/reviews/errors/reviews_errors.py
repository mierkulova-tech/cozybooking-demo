from apps.common.exceptions.base import (
    ApplicationError,
    NoContentError,
    PermissionDeniedError,
)


class ReservationNotFoundError(NoContentError):
    default_detail = "Бронирование не найдено."
    default_code = "reservation_not_found"


class NotReservationOwnerError(PermissionDeniedError):
    default_detail = "Оставить отзыв может только автор бронирования."
    default_code = "not_reservation_owner"


class StayNotCompletedError(ApplicationError):
    default_detail = "Отзыв можно оставить только после состоявшегося проживания."
    default_code = "stay_not_completed"


class AlreadyReviewedError(ApplicationError):
    default_detail = "Отзыв по этому бронированию уже оставлен."
    default_code = "already_reviewed"
