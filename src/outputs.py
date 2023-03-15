import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, DEFAULT_OUTPUT, FILE_OUTPUT,
                       PRETTY_OUTPUT)

CSV_SAVE_SUCCEED = 'Файл с результатами был сохранён: {file_path}'


def default_output(results, *args):
    """Печатаем список results построчно"""
    for row in results:
        print(*row)


def pretty_output(results, *args):
    """Вывод результатов в формате PrettyTable"""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Сохранение результатов в csv файле"""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, csv.unix_dialect)
        writer.writerows(results)
    logging.info(CSV_SAVE_SUCCEED.format(file_path=file_path))


OUTPUT_FORMAT = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    DEFAULT_OUTPUT: default_output
}


def control_output(results, cli_args):
    """Контроль отображения результатов парсинга"""
    OUTPUT_FORMAT.get(cli_args.output)(results, cli_args)
