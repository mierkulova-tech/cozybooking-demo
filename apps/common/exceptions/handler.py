"""Custom DRF exception handler that wraps error responses in a consistent shape."""

from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """Wrap DRF's default error response in a consistent {"error": {...}} shape.

    Args:
        exc: The exception raised during request processing.
        context: The DRF view context in which the exception occurred.

    Returns:
        The modified Response with a standardized "error" envelope
        (containing "code" and "detail"), or None if DRF's default
        handler could not process the exception.
    """
    response = drf_exception_handler(exc, context)

    if response is None:
        return response

    code = getattr(exc, "default_code", "error")
    response.data = {
        "error": {
            "code": code,
            "detail": response.data,
        }
    }
    return response
