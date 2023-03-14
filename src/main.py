import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_PYTHON_URL
from outputs import control_output
from utils import find_tag, get_response, pep_page_check_status


def pep(session):
    """Собирает информацию о статусах PEP"""
    peps_main_page = PEPS_PYTHON_URL
    temp_results = {}
    results = [('Статус', 'Количество')]
    total_pep = 0
    response = get_response(session, peps_main_page)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    index_by_category = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'}
    )
    table_class = find_tag(
        index_by_category,
        'table', attrs={'class': 'pep-zero-table docutils align-default'}
    )
    tbody = find_tag(table_class, 'tbody')
    trclass = tbody.find_all('tr')
    for tr_tag in tqdm(trclass):
        status = find_tag(tr_tag, 'abbr')
        href = find_tag(tr_tag, 'a')['href']
        preview_status = status.text[1:]
        status_tuple = EXPECTED_STATUS[preview_status]

        pep_link = urljoin(peps_main_page, href)
        pep_page_status = pep_page_check_status(session, pep_link)

        if pep_page_status not in status_tuple:
            logging.info(
                f'Несовпадающие статусы: \n'
                f'{pep_link} \n'
                f'Статус в карточке: {pep_page_status} \n'
                f'Ожидаемые статусы: {status_tuple} \n'
            )
        if pep_page_status in temp_results:
            temp_results[pep_page_status] += 1
        else:
            temp_results[pep_page_status] = 1
        total_pep += 1
    temp_results['Total'] = total_pep
    results += list(temp_results.items())
    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((version_link, h1.text, dl_text))
    return result


def latest_versions(session):
    REG_EX = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('ничего не нашлось')

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
    REG_EX = r'.+pdf-a4\.zip$'
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, 'lxml')

    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', {'href': re.compile(REG_EX)})

    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(
        f'Архив с документацией был загружен и сохранен: {archive_path}'
    )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
