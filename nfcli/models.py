from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter
from typing import Dict, List, Optional

import arrow
from rich.console import Console
from rich.text import Text

from nfcli.printers import FleetPrinter, MissilePrinter, Printable, ShipPrinter, print_any, write_any


class Lobby:
    """Plain object for lobby."""

    def __init__(self, in_progress: int, has_password: int) -> None:
        self.in_progress = in_progress == 1
        self.has_password = has_password == 1


class Lobbies:
    """Parses and provides additional lobby operations."""

    def __init__(self, timestamp: int, author: str, lobby_data: Optional[str] = None) -> None:
        self.timestamp = timestamp
        self.author = author
        self.lobbies: Optional[List[Lobby]] = None
        if lobby_data is not None:
            self.lobbies = self._parse_data(lobby_data)

    @classmethod
    def _parse_data(cls, lobby_data: str) -> List[Lobbies]:
        lobbies = json.loads(lobby_data)
        lobby_list = []
        for lobby in lobbies:
            lobby_list.append(Lobby(lobby["i"], lobby["h"]))
        return lobby_list

    def __str__(self) -> str:
        if not self.is_valid:
            return (
                "I don't have any recent lobby data at hand. "
                "Perhaps you could help by running our data gathering mod? "
                "Ask @Jaghaimo#8364 for details."
            )
        total_lobbies = len(self.lobbies)
        if total_lobbies == 0:
            return (
                f"As of {self.time} there were no lobbies present in the game.\n"
                f"*Data kindly provided by {self.author}'s client.*"
            )
        lobby_or_lobbies = "there was one lobby" if total_lobbies == 1 else f"there were {total_lobbies} lobbies"
        open_lobbies = len(self.open)
        open_private = len(self.with_password(self.open))
        open_public = open_lobbies - open_private
        in_progress = len(self.in_progress)
        in_progress_private = len(self.with_password(self.in_progress))
        in_progress_public = in_progress - in_progress_private
        return (
            f"As of {self.time} {lobby_or_lobbies} present in the game.\n"
            "```yaml\n"
            f"Open Lobbies : {open_lobbies} [{open_public} public and {open_private} private]\n"
            f" In Progress : {in_progress} [{in_progress_public} public and {in_progress_private} private]\n"
            "```"
            f"*Data kindly provided by {self.author}'s client.*"
        )

    @property
    def is_valid(self) -> bool:
        if self.lobbies is None:
            return False

        timedelta = arrow.now() - arrow.get(self.timestamp)
        return timedelta.seconds < 1800

    @property
    def time(self) -> str:
        return arrow.get(self.timestamp).humanize()

    @property
    def open(self) -> List[Lobby]:
        return [lobby for lobby in self.lobbies if not lobby.in_progress]

    @property
    def in_progress(self) -> List[Lobby]:
        return [lobby for lobby in self.lobbies if lobby.in_progress]

    def with_password(self, lobbies: Optional[List[Lobby]] = None) -> List[Lobby]:
        if lobbies is None:
            lobbies = self.lobbies
        return [lobby for lobby in lobbies if lobby.has_password]


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


class Missile(Named, Printable):
    """Models content of a missile template."""

    def __init__(
        self, designation: str, nickname: str, description: str, long_description: str, cost: int, body_key: str
    ) -> None:
        super().__init__(body_key)
        self.designation = designation
        self.nickname = nickname
        self.full_name = f"{designation} {nickname}"
        self.description = description
        self.cost = cost
        full_stats = [stats.replace("\n\t", " ") for stats in long_description.split("\n\n")]
        (
            self.long_description,
            self.avionics,
            self.flight_characteristics,
            self.damage,
            self.additional_stats,
        ) = full_stats

    @property
    def size(self) -> str:
        return re.search("[1-9]+", self.name).group()

    @property
    def title(self) -> str:
        return f"{self.full_name} is a size {self.size} missile that costs {self.cost} points."

    @property
    def text(self) -> str:
        return Text.from_markup(self.title).plain + "."

    @property
    def is_valid(self):
        return True

    def print(self, console: Console, with_title: bool, mods: List[str]):
        print_any(MissilePrinter(console), self, mods, with_title)

    def write(self, filename: str):
        title = Text.from_markup(self.title).plain
        write_any(self, 3, title, filename)


class Ship(Named, Printable):
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
    def name(self):
        return self._name

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
        return f"'{self.name}' is {a_or_an} {self.hull} that costs {self.cost} points"

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

    def print(self, console: Console, with_title: bool, mods: List[str]):
        print_any(ShipPrinter(console), self, mods, with_title)

    def write(self, filename: str):
        title = Text.from_markup(self.title).plain
        write_any(self, 3, title, filename)


class Fleet(Named, Printable):
    def __init__(self, name: str, points: int, faction: str):
        super().__init__(name)
        self.points = points
        self.faction = faction
        self._ships: List[Ship] = []
        self._missiles: List[Missile] = []

    @property
    def ships(self) -> List[Ship]:
        return sorted(self._ships, key=lambda ship: int(ship.cost), reverse=True)

    @property
    def missiles(self) -> List[Missile]:
        return sorted(self._missiles, key=lambda missile: missile.full_name)

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
        return len(self._ships)

    @property
    def title(self) -> str:
        ship_or_ships = "ships that cost" if self.n_ships > 1 else "ship which costs"
        return f"Fleet '{self.name}' is composed of {self.n_ships} {ship_or_ships} {self.points} points"

    @property
    def text(self) -> str:
        return self.ship_list + self.missile_list

    @property
    def ship_list(self) -> str:
        longest_name = max([len(ship.name) for ship in self.ships])
        ship_list = [f"{ship.name.rjust(longest_name)} : {ship.hull} [{ship.tags}]" for ship in self.ships]
        return f"{self.title}:\n```yaml\n" + "\n".join(ship_list) + "\n```"

    @property
    def missile_list(self) -> str:
        if not self._missiles:
            return ""
        longest_name = max([len(missile.full_name) for missile in self.missiles])
        missile_list = [
            f"{missile.full_name.rjust(longest_name)} : {missile.description} [{missile.cost}pts]"
            for missile in self.missiles
        ]
        title = (
            "This fleet uses only one missile type"
            if len(missile_list) == 1
            else f"This fleet uses {len(missile_list)} different missile types"
        )
        return f"{title}:\n```yaml\n" + "\n".join(missile_list) + "\n```"

    def add_ship(self, ship: Ship) -> None:
        self._ships.append(ship)

    def add_missile(self, missile: Missile) -> None:
        self._missiles.append(missile)

    def print(self, console: Console, with_title: bool, mods: List[str] = []):
        print_any(FleetPrinter(console), self, mods, with_title)

    def write(self, filename: str):
        write_any(self, self.n_ships, self.title, filename)
