import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_DOC_URL, EXPECTED_STATUS,
                       MAIN_DOC_URL, PEPS_PYTHON_URL, WHATS_NEW_URL)
from exceptions import (ERROR, NOT_FOUND, UNEXPECTED_STATUS,
                        ParserFindTagException)
from outputs import control_output
from utils import find_tag, get_pep_page_status, get_soup

START = 'Парсер запущен!'
ARGS = 'Аргументы командной строки: {args}'
DOWNLOAD_SUCCEED = ('Архив с документацией был'
                    'загружен и сохранен: {archive_path}')
FINISH = 'Парсер завершил работу.'


def pep(session):
    """Собирает информацию о статусах PEP"""
    peps_main_page = PEPS_PYTHON_URL
    temp_results = {}
    results = [('Статус', 'Количество')]
    total_pep = 0
    logs = []
    soup = get_soup(session, peps_main_page)
    trclass = soup.select('#numerical-index table.pep-zero-table tbody tr')
    if not trclass:
        raise ParserFindTagException(NOT_FOUND)
    for tr_tag in tqdm(trclass):
        status = find_tag(tr_tag, 'abbr')
        href = find_tag(tr_tag, 'a')['href']
        preview_status = status.text[1:]
        status_tuple = EXPECTED_STATUS[preview_status]

        pep_link = urljoin(peps_main_page, href)
        pep_page_status = get_pep_page_status(session, pep_link)

        if pep_page_status not in status_tuple:
            logs.append(
                UNEXPECTED_STATUS.format(
                 pep_link=pep_link,
                 pep_page_status=pep_page_status,
                 status_tuple=status_tuple
                )
            )
        if pep_page_status in temp_results:
            temp_results[pep_page_status] += 1
        else:
            temp_results[pep_page_status] = 1
        total_pep += 1
    list(map(logging.warning, logs))
    temp_results['Total'] = total_pep
    results += list(temp_results.items())
    return results


def whats_new(session):
    """Собирает информацию о новых статьях"""
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    soup = get_soup(session, WHATS_NEW_URL)
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    if not sections_by_python:
        raise ParserFindTagException(NOT_FOUND)
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag["href"]
        version_link = urljoin(WHATS_NEW_URL, href)
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((version_link, h1.text, dl_text))
    return result


def latest_versions(session):
    """Собирает информацию о последних версиях документации"""
    REG_EX = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    soup = get_soup(session, MAIN_DOC_URL)
    ul_tags = soup.select('div.sphinxsidebarwrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException(NOT_FOUND)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = REG_EX
    for a_tag in a_tags:
        data = re.search(pattern, a_tag.text)
        if data is not None:
            link = a_tag['href']
            version, status = data.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """Скачивает архив с документацией"""
    soup = get_soup(session, DOWNLOAD_DOC_URL)
    pdf_a4_link = soup.select_one(
        'table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(DOWNLOAD_DOC_URL, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_SUCCEED.format(archive_path=archive_path))


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(ARGS.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(ERROR.format(error=error))
    logging.info(FINISH)


if __name__ == '__main__':
    main()
