import json
import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rich.theme import Theme

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})

# Early localization support
__localization_file = "data/en_ui.json"
__loc_pattern = re.compile(r"\$([a-zA-Z0-9_]+)")
__loc_data = {}
with open(__localization_file, encoding="utf-8-sig") as f:
    try:
        __loc_data = json.load(f)
    except json.JSONDecodeError:
        logging.error("Failed to parse localization file...")



def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def init_debugger():
    if os.getenv("DEBUG") == "True":
        import multiprocessing

        current_process_pid = multiprocessing.current_process().pid
        if current_process_pid is not None and current_process_pid > 1:
            import debugpy

            debugpy.listen(("localhost", 9000))
            print("Debugger is ready to be attached", flush=True)
            debugpy.wait_for_client()
            print("Debugger is now attached", flush=True)


def init_logger(filename: str | None, level: int):
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    handlers = [stream_handler]
    if filename:
        file_handler = TimedRotatingFileHandler(filename, when="d", interval=1, backupCount=7)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers, force=True)


def load_path(path: str) -> str:
    with open(path) as f:
        return f.read()


def localize(content: str):
    def replacer(_match: re.Match[str]) -> str:
        key = _match.group(1)
        return __loc_data.get(key, _match.group(0))

    return __loc_pattern.sub(replacer, content)


def strip_tags(string: str) -> str:
    return re.sub("<[^<]+?>", "", string).strip()


init_debugger()
