from apps.common.exceptions.base import ApplicationError


class EmailAlreadyExistsError(ApplicationError):
    default_detail = "Пользователь с таким email уже существует."
    default_code = "email_already_exists"


class InvalidCredentialsError(ApplicationError):
    default_detail = "Неверный email или пароль."
    default_code = "invalid_credentials"
