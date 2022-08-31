import logging
import re
from logging.handlers import TimedRotatingFileHandler
from os import getenv
from pathlib import Path

from rich.theme import Theme

DATA_DIR = "data"
WIKI_DIR = "wiki"

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})


def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def init_debugger():
    if getenv("DEBUG") == "True":
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
            import debugpy

            debugpy.listen(("localhost", 9000))
            print("Debugger is ready to be attached, press F5", flush=True)
            debugpy.wait_for_client()
            print("Visual Studio Code debugger is now attached", flush=True)


def init_logger(filename: str, level: int):
    file_handler = TimedRotatingFileHandler(filename, when="d", interval=1, backupCount=7)
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG, handlers=[stream_handler, file_handler], force=True)


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def strip_tags(string: str) -> str:
    return re.sub("<[^<]+?>", "", string).strip()


init_debugger()
