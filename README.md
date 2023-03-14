### Парсер сайтов по документации Python и стандартам PEP

Список поддерживаемых сайтов:

https://docs.python.org/3/

https://peps.python.org/

### Инструкция по запуску:
**Клонируйте репозиторий:**
```
git clone git@github.com:VadimVolkovsky/bs4_parser_pep.git
```

**Установите и активируйте виртуальное окружение:**
для MacOS:
```
python3 -m venv venv
```

для Windows:
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```
**Установите зависимости из файла requirements.txt:**
```
pip install -r requirements.txt
```

**Перейдите в папку "src":**
```
cd src/
```

**Запустите парсер в одном из режимов:**

```
python main.py <parser_mode> <args>
```

### Режимы парсера:
При запуске парсера необходимо выбрать один из режимов <parser_mode>:

**whats-new**
Парсинг последних обновлений с сайта
```
python main.py whats-new <args>
```

**latest-versions**
Парсинг последних версий документации
```
python main.py latest_versions <args>
```

**download**
Загрузка и сохранение архива с документацией
```
python main.py download <args>
```

**pep**
Парсинг статусов PEP
```
python main.py pep <args>
```

### Аргументы парсера:
**При запуске парсера можно указать дополнительные аргументы <args>:**

Вывести информацию о парсере:
```
python main.py <parser_mode> -h
python main.py <parser_mode> --help
```

Очистить кеш:
```
python main.py <parser_mode> -c
python main.py <parser_mode> --clear-cache
```

Настроить режим отображения результатов:
Сохранение результатов в CSV файл:
```
python main.py <parser_mode> --output file
```
Отображение результатов в табличном формате в консоли:
```
python main.py <parser_mode> --output pretty
```

Если не указывать аргумент --output, результат парсинга будет выведен в консоль:
(кроме парсера download)
```
python main.py <parser_mode>
```


### Автор проекта:

**Vadim Volkovsky**
