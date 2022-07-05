import logging
import math
from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Tuple, Type

from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS, nfc_theme

if TYPE_CHECKING:
    from nfcli.model import Fleet, Ship, ShipFleetType, Socket


class FleetPrinter(ABC):
    def __init__(self, column_width: int, console: Console, no_title: Optional[bool] = False):
        self.column_width = column_width
        self.console = console
        self.no_title = no_title

    def print(self, fleet: "Fleet"):
        if not self.no_title:
            self.console.print(Panel(Text(fleet.title.center(self.console.width), style="white"), style="orange"))

    def add_components(self, tree: Tree, socket: "Socket"):
        for content in socket.contents:
            tree.add(f"{content.name} x{content.quantity} ", style="i d")

    def get_sockets(self, title: str, sockets: List["Socket"], color: Optional[str] = "white") -> Group:
        elements = [Rule(Text(f"{title}", style="orange"), style="orange")]
        for socket in sockets:
            slot_split = socket.slot_name.split(" ")
            slot_name = slot_split[-1]
            just_size = 7 if int(slot_name) < 10 else 6
            slot_size = "x".join([str(size) for size in socket.slot_size]).rjust(just_size)
            slot_info = f"[orange]{slot_name}[/orange] [grey]{slot_size}[/grey]"
            tree = Tree(
                Text.from_markup(f"{slot_info} {socket.name}", overflow="ignore"),
                style=color,
                guide_style="dim",
            )
            self.add_components(tree, socket)
            elements.append(tree)
        if not sockets:
            elements.append("[grey]" + "<EMPTY>".center(self.column_width) + "[/grey]")
        return Group(*elements)


class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: "Ship") -> RenderableType:
        line1 = ship.name.center(self.column_width)
        line2 = f"{ship.hull} ({ship.cost})".center(self.column_width)
        text = f"\n[b]{line1}[/b]\n{line2}"
        mountings = self.get_sockets("Mountings", ship.mountings)
        compartments = self.get_sockets("Compartments", ship.compartments)
        modules = self.get_sockets("Modules", ship.modules)
        group = Group(text, mountings, compartments, modules)
        return Padding(group, (0, 1))

    def print(self, fleet: "Fleet"):
        super().print(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, width=self.column_width, padding=(0, 0)))


class StackPrinter(FleetPrinter):
    def get_ship(self, ship: "Ship", no_ship_title: Optional[bool] = False) -> RenderableType:
        props = ["mountings", "compartments", "modules"]
        sockets = [Padding(self.get_sockets(prop.title(), getattr(ship, prop)), (0, 1)) for prop in props]
        if not no_ship_title:
            self.console.print("\n" + ship.title.center(self.console.width), highlight=False)
        return Columns(sockets, width=self.column_width, padding=(0, 0))

    def print(self, fleet: "Fleet"):
        super().print(fleet)
        for ship in fleet.ships:
            self.console.print(self.get_ship(ship))


def determine_printer(num_of_ships: int) -> Tuple[int, Type[FleetPrinter]]:
    if num_of_ships < 4:
        return (STACK_COLUMNS * COLUMN_WIDTH, StackPrinter)

    width = num_of_ships * COLUMN_WIDTH
    if num_of_ships > 5:
        width = math.ceil(num_of_ships / 2) * COLUMN_WIDTH

    return (width, ColumnPrinter)


def fleet_printer_factory(printer: str, num_of_ships: int):
    console = Console(theme=nfc_theme)
    if printer == "auto":
        style = "stack" if console.width < num_of_ships * COLUMN_WIDTH else "column"
        style = style if num_of_ships > 3 else "stack"
        return fleet_printer_factory(style, num_of_ships)

    if printer == "column":
        logging.debug("Returning ColumnPrinter")
        column_width = min(COLUMN_WIDTH, console.width)
        console.width = min(num_of_ships * column_width, console.width)
        return ColumnPrinter(column_width, console)

    if printer == "stack":
        logging.debug("Returning StackPrinter")
        console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, console.width), console.height)
        column_width = int(console.width / STACK_COLUMNS)
        return StackPrinter(column_width, console)

    logging.warn("Unknown printer requested, returning 'auto'")
    return fleet_printer_factory("auto", num_of_ships)


def printer_factory(printer: str, entity: "ShipFleetType"):
    if entity.__class__.__name__ == "Fleet":
        return fleet_printer_factory(printer, entity.n_ships)

    return fleet_printer_factory("stack", 1)
