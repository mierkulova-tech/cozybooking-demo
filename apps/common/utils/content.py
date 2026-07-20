"""Helper utilities for checking content availability.

This module provides helper functions to validate whether content is present
and raise appropriate exceptions when content is missing or empty.
"""

from apps.common.exceptions.base import NoContentError


def check_content_helper(content):
    """Validate that the provided content is neither None nor empty.

    Args:
        content: The content object, collection, or queryset to check.

    Returns:
        The validated content if present.

    Raises:
        NoContentError: If content is None or has a length of zero.
    """
    if content is None:
        raise NoContentError()
    if hasattr(content, "__len__") and len(content) == 0:
        raise NoContentError()
    return content
