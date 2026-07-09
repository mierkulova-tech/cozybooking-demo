from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
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
