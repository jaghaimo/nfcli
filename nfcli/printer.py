import logging
from abc import ABC, abstractmethod
from typing import List

from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.text import Text
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


class FleetPrinter(ABC):
    @abstractmethod
    def print(self, fleet: Fleet) -> Console:
        console = Console()
        console.print()
        return console

class ColumnPrinter(FleetPrinter):
    def add_components(self, tree: Tree, socket: Socket):
        for content in socket.contents:
            tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="i")


    def add_sockets(self, tree: Tree, sockets: List[Socket], color: str):
        for socket in sockets:
            subtree = tree.add(f"{socket.name} ", style=color)
            self.add_components(subtree, socket)

    def get_ship(self, ship: Ship):
        tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="r"))
        self.add_sockets(tree, ship.mountings, "red")
        self.add_sockets(tree, ship.compartments, "green")
        self.add_sockets(tree, ship.modules, "blue")
        self.add_sockets(tree, ship.invalid, "white")
        return Padding(tree, (0, 1))

    def print(self, fleet: Fleet):
        console = super().print(fleet)
        ship_or_ships = "ships" if len(fleet.ships) > 1 else "ship"
        title = Text(f"Fleet '{fleet.name}' contains {len(fleet.ships)} {ship_or_ships} and costs {fleet.points} points\n", style="i")
        ships = [self.get_ship(ship) for ship in fleet.ships]
        console.print(Columns(ships, title=title))

class PanelPrinter(FleetPrinter):
    def print(self, fleet: Fleet):
        console = super().print(fleet)

def printer_factory(printer: str):
    if printer == "column" or printer == "default":
        logging.debug("Returning ColumnPrinter")
        return ColumnPrinter()

    if printer == "panel":
        logging.debug("Returning PanelPrinter")
        return PanelPrinter()

    logging.warn(f"Could not determine printer class for {printer}, returning PanelPrinter")
    return printer_factory("panel")
