import logging
import tempfile
from abc import abstractmethod, abstractproperty
from pathlib import Path

import cairosvg
import xmltodict
from rich.console import Console

from nfcli import nfc_theme
from nfcli.printers import Printable, determine_width


class Writeable:
    @abstractproperty
    def is_valid(self):
        raise NotImplementedError

    @abstractmethod
    def write(self, filename: str):
        raise NotImplementedError


def determine_output_png(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"


def get_temp_filename(ext: str) -> str:
    return tempfile.mktemp() + ext


def write_file(console: Console, title: str, png_file: str):
    svg_content = console.export_svg(title=title, clear=True)
    svg_dict = xmltodict.parse(svg_content)
    try:
        del svg_dict["svg"]["g"][0]
    except KeyError:
        logging.warning("Failed to clean SVG output.")
    console.set_alt_screen(False)
    cairosvg.svg2png(bytestring=xmltodict.unparse(svg_dict), write_to=png_file)


def write_any(printable: Printable, num_of_columns: int, title: str, png_file: str):
    width = determine_width(num_of_columns)
    console = Console(width=width, record=True, theme=nfc_theme, force_terminal=True)
    console.set_alt_screen(True)
    printable.print(console)
    write_file(console, title, png_file)
