import math
import os
import tempfile
from pathlib import Path
from typing import List, TextIO, Tuple, Type

import cairosvg
from rich.console import Console

from nfcli import COLUMN_WIDTH, STACK_COLUMNS
from nfcli.model import Fleet
from nfcli.printer import ColumnPrinter, FleetPrinter, StackPrinter


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


def get_printer(num_of_ships: int) -> Tuple[int, Type[FleetPrinter]]:
    if num_of_ships < 4:
        return (STACK_COLUMNS * COLUMN_WIDTH, StackPrinter)

    width = num_of_ships * COLUMN_WIDTH
    if num_of_ships > 5:
        width = math.ceil(num_of_ships / 2) * COLUMN_WIDTH

    return (width, ColumnPrinter)


def write_fleet(fleet: Fleet, png_file: str):
    width, printer_class = get_printer(len(fleet.ships))
    console = Console(width=width, record=True, color_system="truecolor", force_terminal=True)
    console.set_alt_screen(True)
    printer = printer_class(COLUMN_WIDTH, console, no_title=True)
    printer.print(fleet)
    title = printer.get_title(fleet).plain
    svg_content = console.export_svg(title=title, clear=True)
    console.set_alt_screen(False)
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
