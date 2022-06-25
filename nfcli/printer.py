from typing import List

from nfcli.model import Fleet, Ship, Socket


def print_contents(contents: List[str]):
    for content in contents:
        print(f"   {content}")

def print_sockets(sockets: List[Socket]):
    for socket in sockets:
        symbol = "+" if socket.contents else "-"
        print(f" {symbol} {socket.name}")
        print_contents(socket.contents)

def print_ship(ship: Ship):
    print("")
    print(f"Ship Name: {ship.name}")
    print(f"Ship Hull: {ship.hull}")
    print(f"Ship Cost: {ship.cost}")
    if ship.sockets:
        print_sockets(ship.sockets)

def print_fleet(fleet: Fleet):
    print(f"Fleet Name: {fleet.name}")
    print(f"Fleet Faction: {fleet.faction}")
    print(f"Fleet Points: {fleet.points}")
    for ship in fleet.ships:
        print_ship(ship)

