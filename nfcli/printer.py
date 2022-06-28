import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from rich.columns import Columns
from rich.console import Console, RenderableType, TextType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


class FleetPrinter(ABC):
    def __init__(self, column_width: int, console: Console) -> None:
        self.column_width = column_width
        self.console = console

    @abstractmethod
    def print(self, fleet: Fleet):
        raise NotImplemented

    def print_title(self, fleet: Fleet):
        desired_width = min(self.column_width * len(fleet.ships), self.console.width)
        self.console.print(Panel(self.get_title(fleet).plain, width=desired_width, style="i"))

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

class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: Ship) -> RenderableType:
        tree = Tree(
            Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="r")
        )
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return Padding(tree, (0, 1))


    def print(self, fleet: Fleet):
        self.print_title(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, width=self.column_width, padding=(0, 0)))


class StackPrinter(FleetPrinter):
    def __init__(self, column_width: int, console: Console, no_title: Optional[bool] = False):
        super().__init__(column_width, console)
        self.no_title = no_title

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
        sockets = [
            self.get_sockets(ship, prop, color) for (prop, color) in props_colors
        ]
        return Columns(
            sockets,
            title=f"'{ship.name}' is a {ship.hull} that costs {ship.cost} points",
            width=width,
            padding=(0, 0),
        )

    def print(self, fleet: Fleet):
        if not self.no_title:
            self.print_title(fleet)
        for ship in fleet.ships:
            self.console.print(self.get_ship(ship, self.column_width))


def printer_factory(printer: str, num_of_ships: int):
    console = Console()
    if printer == "auto":
        style = "stack" if console.width < num_of_ships * 33 else "column"
        style = style if num_of_ships > 3 else "stack"
        return printer_factory(style, num_of_ships)

    if printer == "column":
        logging.debug("Returning ColumnPrinter")
        column_width = min(40, console.width)
        return ColumnPrinter(column_width, console)

    if printer == "stack":
        logging.debug("Returning StackPrinter")
        console.size = (min(120, console.width), console.height)
        column_width = int(console.width / 3) 
        return StackPrinter(column_width, console)

    logging.warn(f"Unknown printer requested, returning 'auto'")
    return printer_factory("auto", num_of_ships)
