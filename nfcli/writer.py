import cairosvg
from rich.console import Console

from nfcli.model import Fleet
from nfcli.printer import StackPrinter


def write_fleet(fleet: Fleet, fleet_file: str) -> str:
    console = Console(width=120, record=True)
    printer = StackPrinter(38, console)
    printer.print(fleet)
    svg_file = fleet_file + ".svg"
    console.save_svg(svg_file)
    png_file = fleet_file + ".png"
    cairosvg.svg2png(url=svg_file, write_to=png_file)
    return png_file
