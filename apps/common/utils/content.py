"""
Хелпер проверки наличия контента.

Сервисы вызывают check_content_helper(...) после запроса в БД: если
данных нет — вместо тихого пустого ответа поднимается NoContentError
(404). Одна точка правды на весь проект.
"""

from apps.common.exceptions.base import NoContentError


def check_content_helper(content):
    """
    Бросает NoContentError, если content «пустой».

    Работает и с queryset/list (пустой список), и с одиночным объектом
    (None). Числа/ноль сознательно не проверяем — здесь речь про наличие
    записей, а не про их значение.
    """
    if content is None:
        raise NoContentError()
    if hasattr(content, "__len__") and len(content) == 0:
        raise NoContentError()
    return content
