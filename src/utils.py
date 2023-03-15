import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import (BROKEN_URL, RESPONSE_IS_NONE, TAG_NOT_FOUND,
                        ParserFindTagException)


def get_response(session, url, encoding='utf-8'):
    """Парсинг url и перехват исключения если url недоступен"""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        logging.exception(
            BROKEN_URL.format(url=url),
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Поиск тега в супе и перехват исключения если тег не найден"""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        logging.error(
            TAG_NOT_FOUND.format(tag=tag, attrs=attrs), stack_info=True
        )
        raise ParserFindTagException(
            TAG_NOT_FOUND.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def get_pep_page_status(session, url):
    """Парсит статус PEP на его странице"""
    soup = get_soup(session, url)
    abbr = find_tag(soup, 'abbr')
    return abbr.text


def get_soup(session, url, features='lxml'):
    """Парсит url и возвращает объект супа"""
    response = get_response(session, url)
    if response is None:
        logging.error(RESPONSE_IS_NONE.format(url=url))
        return
    soup = BeautifulSoup(response.text, features)
    return soup
