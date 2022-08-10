import logging
from logging.handlers import TimedRotatingFileHandler

from rich.theme import Theme

from nfcli.debugger import init_debugger

DATA_DIR = "data"
WIKI_DIR = "wiki"

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})

init_debugger()


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def init_logger(filename: str, level: int):
    file_handler = TimedRotatingFileHandler(filename, when="d", interval=1, backupCount=7)
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG, handlers=[stream_handler, file_handler], force=True)
