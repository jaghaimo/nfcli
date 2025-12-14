import logging
import json
import os
import re
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rich.theme import Theme

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})
__localization_file = 'data/en_ui.json'
with open(__localization_file, 'r', encoding='utf-8-sig') as f:
    try:
        __loc_json = json.load(f)
        __loc_data = {
            k.encode('utf-8'): v.encode('utf-8')
            for k, v in __loc_json.items()
        }
    except json.JSONDecodeError as e:
        print("Error: Failed to parse localization file...", flush=True)

__loc_pattern_bytes = re.compile(rb'\$([a-zA-Z0-9_]+)')
__loc_pattern_str = re.compile(r'\$([a-zA-Z0-9_]+)')

def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def init_debugger():
    if os.getenv("DEBUG") == "True":
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
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


def localize(content):
    if type(content) is str:
        pattern = __loc_pattern_str
    else: 
        pattern = __loc_pattern_bytes

    def replacer(match):
        key = match.group(1)
        return __loc_data.get(key, match.group(0))
    return pattern.sub(replacer, content)


def strip_tags(string: str) -> str:
    return re.sub("<[^<]+?>", "", string).strip()


init_debugger()
