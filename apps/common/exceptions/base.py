from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ошибка обработки запроса."
    default_code = "application_error"


class NoContentError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Данные не найдены."
    default_code = "no_content"


class PermissionDeniedError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Недостаточно прав для выполнения действия."
    default_code = "permission_denied"
