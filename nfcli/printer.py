import logging
import math
from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Tuple, Type

from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS

if TYPE_CHECKING:
    from nfcli.model import Fleet, Ship, ShipFleetType, Socket


class FleetPrinter(ABC):
    def __init__(self, column_width: int, console: Console, no_title: Optional[bool] = False):
        self.column_width = column_width
        self.console = console
        self.no_title = no_title

    def print(self, fleet: "Fleet"):
        if not self.no_title:
            self.console.print(Panel(fleet.title, style="i"))

    def add_components(self, tree: Tree, socket: "Socket"):
        for content in socket.contents:
            tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="i")

    def add_sockets(self, tree: Tree, sockets: List["Socket"], color: str):
        for socket in sockets:
            slot_size = "x".join([str(size) for size in socket.slot_size])
            slot_info = f"{socket.slot_name} [{slot_size}]"
            subtree = tree.add(f"{socket.name} \n[dim]{slot_info}[/dim] ", style=color)
            self.add_components(subtree, socket)


class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: "Ship") -> RenderableType:
        tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="r"))
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return Padding(tree, (0, 1))

    def print(self, fleet: "Fleet"):
        super().print(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, width=self.column_width, padding=(0, 0)))


class StackPrinter(FleetPrinter):
    def get_sockets(self, ship: "Ship", prop: str, color: str):
        tree = Tree(Text(f" {prop.title()} ", style="r"))
        self.add_sockets(tree, getattr(ship, prop), color)
        return Padding(tree, (0, 1, 1, 1))

    def get_ship(self, ship: "Ship", no_ship_title: Optional[bool] = False) -> RenderableType:
        props_colors = [
            ("mountings", "red"),
            ("compartments", "green"),
            ("modules", "blue"),
        ]
        sockets = [self.get_sockets(ship, prop, color) for (prop, color) in props_colors]
        title = None if no_ship_title else ship.title
        return Columns(
            sockets,
            title=title,
            width=self.column_width,
            padding=(0, 0),
        )

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
    console = Console()
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

    logging.warn(f"Unknown printer requested, returning 'auto'")
    return fleet_printer_factory("auto", num_of_ships)


def printer_factory(printer: str, entity: "ShipFleetType"):
    if entity.__class__.__name__ == "Fleet":
        return fleet_printer_factory(printer, entity.n_ships)

    return fleet_printer_factory("stack", 1)
