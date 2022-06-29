import logging
import math
from abc import ABC, abstractmethod
from typing import List, Optional

from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS
from nfcli.model import Fleet, Ship, Socket


class FleetPrinter(ABC):
    def __init__(self, column_width: int, console: Console, no_title: Optional[bool] = False):
        self.column_width = column_width
        self.console = console
        self.no_title = no_title

    def print(self, fleet: Fleet):
        if not self.no_title:
            self.print_title(fleet)

    def print_title(self, fleet: Fleet):
        columns_that_fit = min(
            math.floor(self.console.width / self.column_width), self.get_max_columns(fleet)
        )
        desired_width = self.column_width * columns_that_fit
        self.console.print(Panel(self.get_title(fleet), width=desired_width, style="i"))

    def add_components(self, tree: Tree, socket: Socket):
        for content in socket.contents:
            tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="i")

    def add_sockets(self, tree: Tree, sockets: List[Socket], color: str):
        for socket in sockets:
            subtree = tree.add(f"{socket.name} ", style=color)
            self.add_components(subtree, socket)

    def get_title(self, fleet: Fleet) -> Text:
        ship_or_ships = "ships" if len(fleet.ships) > 1 else "ship"
        return Text(
            f"Fleet '{fleet.name}' is composed of {len(fleet.ships)} {ship_or_ships} and costs {fleet.points} points",
            style="i",
        )

    @abstractmethod
    def get_max_columns(self, fleet: Fleet):
        raise NotImplemented


class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: Ship) -> RenderableType:
        tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="r"))
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return Padding(tree, (0, 1))

    def get_max_columns(self, fleet: Fleet):
        return len(fleet.ships)

    def print(self, fleet: Fleet):
        super().print(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, width=self.column_width, padding=(0, 0)))


class StackPrinter(FleetPrinter):
    def get_sockets(self, ship: Ship, prop: str, color: str):
        tree = Tree(Text(f" {prop.title()} ", style="r"))
        self.add_sockets(tree, getattr(ship, prop), color)
        return Padding(tree, (0, 1, 1, 1))

    def get_ship(self, ship: Ship, width: int):
        props_colors = [
            ("mountings", "red"),
            ("compartments", "green"),
            ("modules", "blue"),
        ]
        sockets = [self.get_sockets(ship, prop, color) for (prop, color) in props_colors]
        a_or_an = "an" if ship.hull[0] == "A" else "a"
        return Columns(
            sockets,
            title=f"'{ship.name}' is {a_or_an} {ship.hull} that costs {ship.cost} points",
            width=width,
            padding=(0, 0),
        )

    def get_max_columns(self, fleet: Fleet):
        return STACK_COLUMNS

    def print(self, fleet: Fleet):
        super().print(fleet)
        for ship in fleet.ships:
            self.console.print(self.get_ship(ship, self.column_width))


def printer_factory(printer: str, num_of_ships: int):
    console = Console()
    if printer == "auto":
        style = "stack" if console.width < num_of_ships * COLUMN_WIDTH else "column"
        style = style if num_of_ships > 3 else "stack"
        return printer_factory(style, num_of_ships)

    if printer == "column":
        logging.debug("Returning ColumnPrinter")
        column_width = min(COLUMN_WIDTH, console.width)
        return ColumnPrinter(column_width, console)

    if printer == "stack":
        logging.debug("Returning StackPrinter")
        console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, console.width), console.height)
        column_width = int(console.width / STACK_COLUMNS)
        return StackPrinter(column_width, console)

    logging.warn(f"Unknown printer requested, returning 'auto'")
    return printer_factory("auto", num_of_ships)
