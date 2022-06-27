from __future__ import annotations

from typing import Callable, List

from nfcli.database import db


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
        self.sockets = [] # type: List[Socket]

    def add_socket(self, socket: Socket) -> None:
        self.sockets.append(socket)

    @property
    def mountings(self):
        return self.filter_sockets(db.is_mounting)

    @property
    def compartments(self):
        return self.filter_sockets(db.is_compartment)

    @property
    def modules(self):
        return self.filter_sockets(db.is_module)

    @property
    def invalid(self):
        return self.filter_sockets(db.is_invalid)


    def filter_sockets(self, check: Callable):
        return [socket for socket in self.sockets if check(socket.name)]

class Fleet():
    def __init__(self, name: str, points: int, faction: str):
        self.name = name
        self.points = points
        self.faction = faction
        self.ships = []

    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)
