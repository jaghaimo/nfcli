import logging
import os
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from rich.theme import Theme

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USERNAME = os.getenv("STEAM_USERNAME")

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})


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
