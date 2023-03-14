import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    """Парсинг url и перехват исключения если url недоступен"""
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Поиск тега в супе и перехват исключения если тег не найден"""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def pep_page_check_status(session, url):
    """Парсит статус PEP на его странице"""
    response = get_response(session, url)
    soup = BeautifulSoup(response.text, 'lxml')
    abbr = find_tag(soup, 'abbr')
    return abbr.text
