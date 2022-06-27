from __future__ import annotations

from typing import List


class Content():
    def __init__(self, name: str, quantity: int) -> None:
        self.name = name
        self.quantity = quantity

class Socket():
    def __init__(self, name: str, contents: List[Content]) -> None:
        self.name = name
        self.contents = contents

class Ship():
    def __init__(self, name: str, cost: int, hull: str) -> None:
        self.name = name
        self.cost = cost
        self.hull = hull
        self.sockets = []

    def add_socket(self, socket: Socket) -> None:
        self.sockets.append(socket)


class Fleet():
    def __init__(self, name: str, points: int, faction: str):
        self.name = name
        self.points = points
        self.faction = faction
        self.ships = []

    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)
