from pathlib import Path
from urllib.parse import urljoin

BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOAD_DOC_URL = urljoin(MAIN_DOC_URL, 'download.html')
LOGS_DIR = BASE_DIR / 'logs'
LOG_FILE = LOGS_DIR / 'parser.log'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEPS_PYTHON_URL = 'https://peps.python.org/'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DR_FORMAT = '%d.%m.%Y %H:%M:%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'
DEFAULT_OUTPUT = None
