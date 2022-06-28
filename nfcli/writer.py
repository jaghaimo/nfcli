import cairosvg
from rich.console import Console

from nfcli.model import Fleet
from nfcli.printer import ColumnPrinter, StackPrinter


def write_fleet(fleet: Fleet, fleet_file: str) -> str:
    console = Console(width=120, record=True)
    printer = StackPrinter(38, console, no_title=True)
    printer.print(fleet)
    title_printer = ColumnPrinter(38, console)
    title = title_printer.get_title(fleet).plain
    svg_content = console.export_svg(title=title, clear=True)
    png_file = fleet_file + ".png"
    cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
    return png_file
