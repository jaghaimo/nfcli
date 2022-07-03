import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List, TextIO

import cairosvg
from rich.console import Console

from nfcli import COLUMN_WIDTH, nfc_theme
from nfcli.printer import FleetPrinter, determine_printer

if TYPE_CHECKING:
    from nfcli.model import Fleet, Ship


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


def get_printer(num_of_ships: int) -> FleetPrinter:
    width, printer = determine_printer(num_of_ships)
    console = Console(width=width, record=True, theme=nfc_theme, force_terminal=True)
    console.set_alt_screen(True)
    return printer(COLUMN_WIDTH, console, no_title=True)


def write_file(console: Console, title: str, png_file: str):
    svg_content = console.export_svg(title=title, clear=True)
    console.set_alt_screen(False)
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)


def write_ship(ship: "Ship", png_file: str):
    printer = get_printer(1)
    renderable = printer.get_ship(ship, no_ship_title=True)
    printer.console.print(renderable)
    title = ship.title
    write_file(printer.console, title, png_file)


def write_fleet(fleet: "Fleet", png_file: str):
    printer = get_printer(fleet.n_ships)
    printer.print(fleet)
    title = fleet.title
    write_file(printer.console, title, png_file)
