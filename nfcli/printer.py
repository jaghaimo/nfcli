from typing import List

from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.tree import Tree

from nfcli.model import Fleet, Ship, Socket


def add_components(tree: Tree, socket: Socket):
    for content in socket.contents:
        tree.add(f"{content.name} [yellow]x{content.quantity}[/yellow]")


def add_sockets(tree: Tree, sockets: List[Socket]):
    for socket in sockets:
        subtree = tree.add(f"{socket.name}")
        add_components(subtree, socket)

def get_ship(ship: Ship):
    tree = Tree(f"[red]{ship.name}[/red]\n[green]{ship.hull}[/green]\n[blue]{ship.cost} points[/blue]")
    add_sockets(tree, ship.sockets)
    return tree

def print_fleet(fleet: Fleet):
    console = Console()
    console.print()
    console.print(f"Fleet Name: [cyan]{fleet.name}[/cyan]")
    console.print(f"Total Points: [cyan]{fleet.points}[/cyan]")
    ships = [Padding(get_ship(ship), (1,2)) for ship in fleet.ships]
    console.print(Columns(ships))

