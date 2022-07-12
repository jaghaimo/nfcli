import logging
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List, TextIO

import cairosvg
import xmltodict
from rich.console import Console
from rich.text import Text

from nfcli import COLUMN_WIDTH, nfc_theme
from nfcli.printer import FleetPrinter, determine_printer

if TYPE_CHECKING:
    from nfcli.model import Fleet, Ship


def close_and_delete(open_file: List[TextIO], filename: str):
    open_file.close()
    os.unlink(filename)


def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def get_temp_filename(ext: str) -> str:
    return tempfile.mktemp() + ext


def get_printer(num_of_ships: int, is_valid: bool) -> FleetPrinter:
    width, printer = determine_printer(num_of_ships, is_valid)
    console = Console(width=width, record=True, theme=nfc_theme, force_terminal=True)
    console.set_alt_screen(True)
    return printer(COLUMN_WIDTH, console, no_title=True)


def write_file(console: Console, title: str, png_file: str):
    svg_content = console.export_svg(title=title, clear=True)
    svg_dict = xmltodict.parse(svg_content)
    try:
        del svg_dict["svg"]["g"][0]
    except KeyError:
        logging.warning("Failed to clean SVG output.")
    console.set_alt_screen(False)
    cairosvg.svg2png(bytestring=xmltodict.unparse(svg_dict), write_to=png_file)


def write_ship(ship: "Ship", png_file: str):
    printer = get_printer(1, ship.is_valid)
    renderable = printer.get_ship(ship, no_ship_title=True)
    printer.console.print(renderable)
    title = Text.from_markup(ship.title).plain
    write_file(printer.console, title, png_file)


def write_fleet(fleet: "Fleet", png_file: str):
    printer = get_printer(fleet.n_ships, fleet.is_valid)
    printer.print(fleet)
    title = fleet.title
    write_file(printer.console, title, png_file)
