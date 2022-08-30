import logging
import re
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional

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


def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def init_logger(filename: str, level: int):
    file_handler = TimedRotatingFileHandler(filename, when="d", interval=1, backupCount=7)
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG, handlers=[stream_handler, file_handler], force=True)


def list_to_str(list: List[str]) -> str:
    filtered_list = [element for element in list if element]
    return "\n".join(filtered_list)


def dict_to_str(dictionary: Dict[str, str]) -> str:
    as_list = [f"{key.rjust(27)}: {value}" if value else "" for key, value in dictionary.items()]
    return "\n".join(as_list)


def pad_str(string: str) -> str:
    padded_str = ""
    for line in string.splitlines():
        tokens = line.split(":", maxsplit=2)
        if len(tokens) != 2:
            padded_str += f"{line.strip()}\n"
            continue
        key, value = tokens[0], tokens[1]
        if not value:
            padded_str += f"\n{key.rjust(32 + len(key))}\n"
            continue
        padded_key = key.strip().rjust(30)
        padded_str += f"{padded_key}: {value.strip()}\n"
    return padded_str[:-1]


def str_to_dict(string: Optional[str] = None) -> Dict[str, str]:
    if not string:
        return {}
    new_dict = {}
    for line in string.splitlines():
        tokens = line.split(":", maxsplit=2)
        if len(tokens) != 2:
            continue
        key, value = tokens[0], tokens[1]
        new_dict[sanitize(key)] = strip_tags(value)
    return new_dict


def sanitize(string: str) -> str:
    return string.replace("(", "").replace(")", "").strip()


def strip_tags(string: str) -> str:
    return re.sub("<[^<]+?>", "", string).strip()
