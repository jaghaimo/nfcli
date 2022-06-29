import os
import tempfile
from pathlib import Path
from typing import List, TextIO

import cairosvg
from rich.console import Console

from nfcli.model import Fleet
from nfcli.printer import ColumnPrinter, StackPrinter


def close_all(open_files: List[TextIO]):
    for open_file in open_files:
        open_file.close()


def delete_all(filenames: str):
    for filename in filenames:
        os.unlink(filename)


def determine_output_file(input_fleet: str, ext: str) -> str:
    return Path(input_fleet).stem + ext


def get_temp_filename(ext: str) -> str:
    return tempfile.mktemp() + ext


def write_fleet(fleet: Fleet, png_file: str):
    console = Console(width=120, record=True)
    printer = StackPrinter(38, console, no_title=True)
    printer.print(fleet)
    title_printer = ColumnPrinter(38, console)
    title = title_printer.get_title(fleet).plain
    svg_content = console.export_svg(title=title, clear=True)
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
