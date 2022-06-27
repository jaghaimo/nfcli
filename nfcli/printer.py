from typing import List

from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.text import Text
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


def add_components(tree: Tree, socket: Socket):
    for content in socket.contents:
        tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow] ", style="italic")


def add_sockets(tree: Tree, sockets: List[Socket], color: str):
    for socket in sockets:
        subtree = tree.add(f"{socket.name} ", style=color)
        add_components(subtree, socket)

def get_ship(ship: Ship):
    tree = Tree(Text(f" {ship.name} \n {ship.hull} \n {ship.cost} points ", style="reverse"))
    add_sockets(tree, ship.mountings, "red")
    add_sockets(tree, ship.compartments, "green")
    add_sockets(tree, ship.modules, "blue")
    add_sockets(tree, ship.invalid, "white")
    return tree

def print_fleet(fleet: Fleet):
    console = Console()
    console.print()
    console.print(f"Fleet Name: [cyan]{fleet.name}[/cyan]")
    console.print(f"Total Points: [cyan]{fleet.points}[/cyan]")
    ships = [Padding(get_ship(ship), (1,1)) for ship in fleet.ships]
    console.print(Columns(ships))

