"""Custom application exceptions for user management and authentication.

This module defines domain-specific exception classes extending ApplicationError
to handle duplicate email conflicts and invalid credential errors.
"""

from apps.common.exceptions.base import ApplicationError


class EmailAlreadyExistsError(ApplicationError):
    """Exception raised when attempting to register with an already registered email."""

    default_detail = "A user with this email already exists."
    default_code = "email_already_exists"


class InvalidCredentialsError(ApplicationError):
    """Exception raised when authentication fails due to incorrect credentials."""

    default_detail = "Invalid email or password."
    default_code = "invalid_credentials"
