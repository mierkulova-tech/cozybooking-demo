"""Base application-level exception classes used across all apps."""

from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    """Base exception for domain/business-rule errors (HTTP 400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Request processing error."
    default_code = "application_error"


class NoContentError(ApplicationError):
    """Raised when the requested resource does not exist (HTTP 404)."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Data not found."
    default_code = "no_content"


class PermissionDeniedError(ApplicationError):
    """Raised when the user lacks permission to perform the action (HTTP 403)."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have sufficient permissions to perform this action."
    default_code = "permission_denied"
