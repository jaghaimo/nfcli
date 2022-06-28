import logging
from abc import ABC, abstractmethod
from typing import List

from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


class FleetPrinter(ABC):
    def __init__(self, console: Console) -> None:
        self.console = console

    @abstractmethod
    def print(self, fleet: Fleet):
        raise NotImplemented

    def add_components(self, tree: Tree, socket: Socket):
        for content in socket.contents:
            tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="i")

    def add_sockets(self, tree: Tree, sockets: List[Socket], color: str):
        for socket in sockets:
            subtree = tree.add(f"{socket.name} ", style=color)
            self.add_components(subtree, socket)

class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: Ship) -> RenderableType:
        tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="r"))
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return Padding(tree, (0, 1))

    def get_title(self, fleet: Fleet) -> Text:
        ship_or_ships = "ships" if len(fleet.ships) > 1 else "ship"
        return Text(f"Fleet '{fleet.name}' is composed of {len(fleet.ships)} {ship_or_ships} and costs {fleet.points} points\n", style="i")

    def print(self, fleet: Fleet):
        self.console.print()
        title = self.get_title(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, title=title, equal=True))

class StackPrinter(FleetPrinter):
    def __init__(self, column_width: int, console: Console) -> None:
        super().__init__(console)
        self.column_width = column_width

    def get_sockets(self, ship: Ship, prop: str, color: str):
        tree = Tree(Text(f" {prop.title()} ", style="r"))
        self.add_sockets(tree, getattr(ship, prop), color)
        return Padding(tree, (1, 1))

    def get_ship(self, ship: Ship, width: int):
        props_colors = [("mountings", "red"), ("compartments", "green"), ("modules", "blue")]
        sockets = [self.get_sockets(ship, prop, color) for (prop, color) in props_colors]
        return Columns(sockets, title=f"'{ship.name}', a {ship.cost} points {ship.hull}", width=width, padding=(0, 0))

    def print(self, fleet: Fleet):
        self.console.print()
        self.console.print(Panel(f"Fleet name: [cyan]{fleet.name}[/cyan]\nTotal cost: [cyan]{fleet.points} points[/cyan]\nNumber of ships: [cyan]{len(fleet.ships)}[/cyan]"))
        for ship in fleet.ships:
            self.console.print(self.get_ship(ship, self.column_width))



def printer_factory(printer: str, num_of_ships: int):
    console = Console()
    if printer == "auto":
        style = "stack" if console.width < num_of_ships * 33 else "column"
        return printer_factory(style, num_of_ships)

    if printer == "column":
        logging.debug("Returning ColumnPrinter")
        return ColumnPrinter(console)

    if printer == "stack":
        logging.debug("Returning StackPrinter")
        console.size = (min(120, console.width), console.height)
        column_width = int(console.width / 3) - 1
        return StackPrinter(column_width, console)

    logging.warn(f"Unknown printer requested, returning 'auto'")
    return printer_factory("auto", num_of_ships)
