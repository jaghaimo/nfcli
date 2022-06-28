from pathlib import Path

import cairosvg
from rich.console import Console

from nfcli.model import Fleet
from nfcli.printer import ColumnPrinter, StackPrinter


def determine_output_file(input_fleet: str) -> str:
    return Path(input_fleet).stem + ".png"

def write_fleet(fleet: Fleet, png_file: str):
    console = Console(width=120, record=True)
    printer = StackPrinter(38, console, no_title=True)
    printer.print(fleet)
    title_printer = ColumnPrinter(38, console)
    title = title_printer.get_title(fleet).plain
    svg_content = console.export_svg(title=title, clear=True)
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
