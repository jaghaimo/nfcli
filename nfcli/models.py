from __future__ import annotations

import logging
import math
from collections import Counter
from typing import Dict, List, Optional

from rich.text import Text

from nfcli.printers import Printable, fleet_printer_factory
from nfcli.writers import Writeable, write_fleet, write_ship


class Named:
    """Adds a cleaned, unnamespaced name."""

    def __init__(self, name: str) -> None:
        self._name = str(name)

    @property
    def name(self):
        return self.get_name(self._name)

    @classmethod
    def get_name(cls, name: str) -> str:
        suffix = name.split("/")[-1]
        cleaned = suffix.split("_")[-1]
        return cleaned[0].upper() + cleaned[1:]


class Content(Named):
    """Models content of a socket (ammo in magazine / launcher)."""

    def __init__(self, name: str, quantity: int) -> None:
        super().__init__(name)
        self.quantity = quantity


class Socket(Named):
    """Models simplified socket info from a fleet/ship file."""

    def __init__(self, key: str, name: str, contents: List[Content], tag: Optional[str]) -> None:
        super().__init__(name)
        self.key = key
        self.contents = contents
        self.tag = tag


class Component:
    """Models full component info (socket + db data)."""

    def __init__(self, socket: Socket, number: int, size: str) -> None:
        self.socket = socket
        self.slot_number = number
        self.slot_size = size
        try:
            self.slot_weight = math.prod([int(x) for x in size.split("x")])
        except ValueError:
            self.slot_weight = 1

    @property
    def name(self) -> str:
        return self.socket.name

    @property
    def contents(self) -> List[Content]:
        return self.socket.contents


class Ship(Named, Printable, Writeable):
    def __init__(self, name: str, cost: int, number: int, symbol_option: int, hull: str, data: Dict) -> None:
        super().__init__(name)
        self.cost = cost
        self.number = number
        self.symbol_option = symbol_option
        self._hull = hull
        self.sockets: Dict[str, Socket] = {}
        self._data = data

    def add_socket(self, socket: Socket) -> None:
        self.sockets[socket.key] = socket

    @property
    def hull(self) -> str:
        if "name" in self._data:
            return self._data.get("name")
        return self.get_name(self._hull)

    @property
    def tags(self) -> str:
        if not self.is_valid:
            return ""

        tag_counter = Counter()
        for component in [component for component in self.mountings]:
            tag_counter.update({component.socket.tag: component.slot_weight})
        logging.debug(tag_counter)
        return " ".join([key for key, _ in tag_counter.most_common() if key is not None])

    @property
    def title(self) -> str:
        a_or_an = "an" if self.hull[0] == "A" else "a"
        return f"[b]{self.name}[/b] is {a_or_an} {self.hull} that costs {self.cost} points"

    @property
    def text(self) -> str:
        return Text.from_markup(self.title).plain + "."

    @property
    def is_valid(self) -> bool:
        return bool(self._data)

    @property
    def mountings(self) -> List[Component]:
        return self._get_components("mounts")

    @property
    def compartments(self) -> List[Component]:
        return self._get_components("compartments")

    @property
    def modules(self) -> List[Component]:
        return self._get_components("modules")

    @property
    def components(self) -> List[Component]:
        return [Component(socket, i + 1, "?x?x?") for i, (_, socket) in enumerate(self.sockets.items())]

    def _get_components(self, type: str) -> List[Component]:
        return [
            Component(self._get_socket(key), i + 1, size) for i, (key, size) in enumerate(self._data.get(type).items())
        ]

    def _get_socket(self, key: str) -> Socket:
        if key in self.sockets:
            return self.sockets[key]
        return Socket(key, "[grey]<EMPTY>", [], None)

    def print(self, style: str, mods: List[str]):
        printer = fleet_printer_factory("stack")
        renderable = printer.get_ship(self)
        printer.console.print(renderable)
        printer.print_mods(mods)

    def write(self, filename: str):
        write_ship(self, filename)


class Fleet(Named, Printable, Writeable):
    def __init__(self, name: str, points: int, faction: str):
        super().__init__(name)
        self.points = points
        self.faction = faction
        self.ships: List[Ship] = []

    @property
    def is_valid(self) -> bool:
        return not bool(self.invalid_ships)

    @property
    def valid_ships(self) -> List[Ship]:
        return [ship for ship in self.ships if ship.is_valid]

    @property
    def invalid_ships(self) -> List[Ship]:
        return [ship for ship in self.ships if not ship.is_valid]

    @property
    def n_ships(self) -> int:
        return len(self.ships)

    @property
    def title(self) -> str:
        ship_or_ships = "ships that cost" if self.n_ships > 1 else "ship which costs"
        return f"Fleet '{self.name}' is composed of {self.n_ships} {ship_or_ships} {self.points} points"

    @property
    def text(self) -> str:
        ships_and_costs = {ship.name: f"{ship.hull} [{ship.tags}]" for ship in self.ships}
        longest_name = max([len(name) for name in ships_and_costs.keys()])
        ship_list = [f"{key.rjust(longest_name)} : {value}" for key, value in ships_and_costs.items()]
        return f"{self.title}:\n```yaml\n" + "\n".join(ship_list) + "\n```"

    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)

    def print(self, style: str, mods: List[str]):
        printer = fleet_printer_factory(style, self)
        printer.print(self)
        printer.print_mods(mods)

    def write(self, filename: str):
        write_fleet(self, filename)
