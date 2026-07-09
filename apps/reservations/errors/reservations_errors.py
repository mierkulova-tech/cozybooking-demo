from apps.common.exceptions.base import ApplicationError, PermissionDeniedError


class DateInPastError(ApplicationError):
    default_detail = "Даты бронирования не могут быть в прошлом."
    default_code = "date_in_past"


class StartDateGreaterEndDateError(ApplicationError):
    default_detail = "Дата заезда должна быть раньше даты выезда."
    default_code = "start_date_greater_end_date"


class DateOccupiedError(ApplicationError):
    default_detail = "На выбранные даты объявление уже забронировано."
    default_code = "date_is_occupied"


class CannotBookOwnListingError(ApplicationError):
    default_detail = "Нельзя бронировать собственное объявление."
    default_code = "cannot_book_own_listing"


class ReservationPermissionDeniedError(PermissionDeniedError):
    default_detail = "Нет прав на изменение этого бронирования."
    default_code = "reservation_permission_denied"


class RenterCancelOnlyError(ApplicationError):
    default_detail = "Арендатор может только отменить бронирование."
    default_code = "renter_cancel_only"


class LessorStatusError(ApplicationError):
    default_detail = (
        "Арендодатель может только подтвердить, отклонить или отметить заселение."
    )
    default_code = "lessor_status_invalid"


class InvalidStatusTransitionError(ApplicationError):
    default_detail = "Недопустимый переход статуса бронирования."
    default_code = "invalid_status_transition"


class CantBeCanceledError(ApplicationError):
    default_detail = "Отмена возможна не позднее чем за 2 дня до заезда."
    default_code = "cant_be_canceled"
