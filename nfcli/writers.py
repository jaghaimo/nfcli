import os
import tempfile
from abc import abstractmethod, abstractproperty
from pathlib import Path

import cairosvg
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


def write_any(printable: Printable, num_of_columns: int, title: str, png_file: str):
    width = determine_width(num_of_columns)
    console = Console(width=width, record=True, theme=nfc_theme, force_terminal=True, file=open(os.devnull, "w"))
    printable.print(console, False, [])
    svg_content = console.export_svg(title=title, clear=False)
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
