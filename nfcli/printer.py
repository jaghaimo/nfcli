import logging
from abc import ABC, abstractmethod
from typing import List

from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.text import Text
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


class FleetPrinter(ABC):
    @abstractmethod
    def print(self, fleet: Fleet):
        raise NotImplemented

class ColumnPrinter(FleetPrinter):
    def add_components(self, tree: Tree, socket: Socket):
        for content in socket.contents:
            tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="italic")


    def add_sockets(self, tree: Tree, sockets: List[Socket], color: str):
        for socket in sockets:
            subtree = tree.add(f"{socket.name} ", style=color)
            self.add_components(subtree, socket)

    def get_ship(self, ship: Ship):
        tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="reverse"))
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return tree

    def print(self, fleet: Fleet):
        console = Console()
        console.print()
        console.print(f"Fleet Name: [cyan]{fleet.name}[/cyan]")
        console.print(f"Total Points: [cyan]{fleet.points}[/cyan]")
        ships = [Padding(self.get_ship(ship), (1,1)) for ship in fleet.ships]
        console.print(Columns(ships))


def printer_factory(printer: str):
    if printer == "column" or printer == "default":
        return ColumnPrinter()

    logging.debug(f"Could not determine printer class for {printer}, returning default")
    return printer_factory("default")
