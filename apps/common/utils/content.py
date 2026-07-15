from apps.common.exceptions.base import NoContentError


def check_content_helper(content):
    if content is None:
        raise NoContentError()
    if hasattr(content, "__len__") and len(content) == 0:
        raise NoContentError()
    return content
