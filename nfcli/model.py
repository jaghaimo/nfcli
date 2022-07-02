from __future__ import annotations

from abc import abstractmethod, abstractproperty
from typing import TYPE_CHECKING, Callable, List, Union

from nfcli.database import db
from nfcli.writer import write_fleet, write_ship

if TYPE_CHECKING:
    from nfcli.printer import FleetPrinter, StackPrinter


class Named:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self):
        return db.get_name(self._name)


class Printable:
    @abstractproperty
    def title(self) -> str:
        raise NotImplemented

    @abstractmethod
    def print(self, printer: "FleetPrinter"):
        raise NotImplemented


class Writeable:
    @abstractmethod
    def write(self, filename: str):
        raise NotImplemented


class Content(Named):
    def __init__(self, name: str, quantity: int) -> None:
        super().__init__(name)
        self.quantity = quantity


class Socket(Named):
    def __init__(self, hull: str, key: str, name: str, contents: List[Content]) -> None:
        super().__init__(name)
        self._hull = hull
        self.key = key
        self.contents = contents

    @property
    def slot_name(self) -> str:
        return db.get_socket_attr(self._hull, self.key, "name")

    @property
    def slot_size(self) -> List:
        return db.get_socket_attr(self._hull, self.key, "size")


class Ship(Named, Printable, Writeable):
    def __init__(self, name: str, cost: int, number: int, symbol_option: int, hull: str) -> None:
        super().__init__(name)
        self.cost = cost
        self.number = number
        self.symbol_option = symbol_option
        self._hull = hull
        self.sockets: List[Socket] = []

    def add_socket(self, socket: Socket) -> None:
        self.sockets.append(socket)

    @property
    def hull(self) -> str:
        return db.get_name(self._hull)

    @property
    def title(self) -> str:
        a_or_an = "an" if self.hull[0] == "A" else "a"
        return f"'{self.name}' is {a_or_an} {self.hull} that costs {self.cost} points"

    @property
    def mountings(self) -> List[Socket]:
        return self.filter_sockets(db.is_mounting)

    @property
    def compartments(self) -> List[Socket]:
        return self.filter_sockets(db.is_compartment)

    @property
    def modules(self) -> List[Socket]:
        return self.filter_sockets(db.is_module)

    @property
    def invalid(self) -> List[Socket]:
        return self.filter_sockets(db.is_invalid)

    def filter_sockets(self, check: Callable) -> List[Socket]:
        return [socket for socket in self.sockets if check(socket._name)]

    def print(self, printer: "StackPrinter"):
        renderable = printer.get_ship(self, no_ship_title=True)
        printer.console.print(renderable)

    def write(self, filename: str):
        write_ship(self, filename)


class Fleet(Named, Printable, Writeable):
    def __init__(self, name: str, points: int, faction: str):
        super().__init__(name)
        self.points = points
        self.faction = faction
        self.ships: List[Ship] = []

    @property
    def n_ships(self) -> int:
        return len(self.ships)

    @property
    def title(self) -> str:
        ship_or_ships = "ships that cost" if self.n_ships > 1 else "ship which costs"
        return f"Fleet '{self.name}' is composed of {self.n_ships} {ship_or_ships} {self.points} points"

    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)

    def print(self, printer: "FleetPrinter"):
        printer.print(self)

    def write(self, filename: str):
        write_fleet(self, filename)


ShipFleetType = Union[Ship, Fleet]
