BROKEN_URL = 'Возникла ошибка при загрузке страницы "{url}"'
TAG_NOT_FOUND = 'Не найден тег {tag} {attrs}'
NOT_FOUND = 'Ничего не нашлось'
RESPONSE_IS_NONE = 'Вернулся пустой response при запросе {url}'
ERROR = 'Во время выполнения скрипта возникла ошибка {error}'
UNEXPECTED_STATUS = (
    '\n Несовпадающие статусы: '
    '\n {pep_link} '
    '\n Статус в карточке: {pep_page_status} '
    '\n Ожидаемые статусы: {status_tuple} \n '
)


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не смог найти тег"""
    pass
