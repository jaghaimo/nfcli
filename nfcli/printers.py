from __future__ import annotations

import math
import os
from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING

import cairosvg
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS, nfc_theme

if TYPE_CHECKING:
    from nfcli.models import Component, Fleet, Missile, Ship


class Printable:
    @abstractproperty
    def title(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def text(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def is_valid(self):
        raise NotImplementedError

    @abstractmethod
    def print(self, console: Console, with_title: bool, mods: list[str]):
        raise NotImplementedError

    @abstractmethod
    def write(self, filename: str):
        raise NotImplementedError


class Printer(ABC):
    def __init__(self, console: Console):
        self.console = console

    @abstractmethod
    def print(self, with_title: bool, printable: Printable):
        raise NotImplementedError

    @classmethod
    def get_mods(cls, mods: list[str], begin_quote: str = "", end_quote: str = "") -> str:
        if not mods:
            return ""
        mods_text = "\nMods required:"
        for mod in mods:
            mods_text += f"\n- {begin_quote}https://steamcommunity.com/sharedfiles/filedetails/?id={mod}{end_quote}"
        return mods_text

    def print_mods(self, mods: list[str]):
        if not mods:
            return
        self.console.print(self.get_mods(mods))


class MissilePrinter(Printer):
    def get_section(self, title: str, text: str):
        padded_str = Text.from_markup(pad_str(text))
        return Padding(Group(Rule(Text(title, style="orange"), style="orange"), padded_str), (0, 1))

    def print(self, with_title: bool, missile: Missile):
        column_width = min(2 * COLUMN_WIDTH, self.console.width)
        self.console.width = min(column_width, self.console.width)
        if with_title:
            self.console.print(Panel(Text(missile.title.center(self.console.width), style="white"), style="orange"))
        self.console.print(Padding(Text(missile.long_description + "\n"), (0, 1)))
        self.console.print(self.get_section("Avionics", missile.avionics))
        self.console.print(self.get_section("Flight Characteristics", missile.flight_characteristics))
        self.console.print(self.get_section("Damage", missile.damage))
        self.console.print(self.get_section("Additional Stats", missile.additional_stats))


class ShipPrinter(Printer):
    def add_components(self, tree: Tree, component: Component):
        for content in component.contents:
            tree.add(Text(f"{content.name} x{content.quantity}", overflow="ignore"), style="i d")

    def get_sockets(self, title: str, components: list[Component], color: str = "white") -> Group:
        elements: list[RenderableType] = [Rule(Text(f"{title}", style="orange"), style="orange")]
        for component in components:
            slot_number = str(component.slot_number)
            just_size = 7 if int(slot_number) < 10 else 6
            slot_size = component.slot_size.rjust(just_size)
            slot_info = f"[orange]{slot_number}[/orange] [grey]{slot_size}[/grey]"
            tree = Tree(
                Text.from_markup(f"{slot_info} {component.name}", overflow="ignore"),
                style=color,
                guide_style="dim",
            )
            self.add_components(tree, component)
            elements.append(tree)
        return Group(*elements)

    def get_ship(self, ship: Ship, column_width: int) -> RenderableType:
        if ship.is_valid:
            props = ["mountings", "compartments", "modules"]
            sockets = [Padding(self.get_sockets(prop.title(), getattr(ship, prop)), (0, 1)) for prop in props]
        else:
            sockets = [Padding(self.get_sockets("Components", ship.components), (0, 1))]
            column_width = 3 * column_width
        return Columns(sockets, width=column_width, padding=(0, 0))

    def print(self, with_title: bool, ship: Ship):
        self.console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, self.console.width), self.console.height)
        column_width = int(self.console.width / STACK_COLUMNS)
        if with_title:
            self.console.print(Panel(Text(ship.title.center(self.console.width), style="white"), style="orange"))
        self.console.print(self.get_ship(ship, column_width))


class FleetPrinter(ShipPrinter):
    def get_ship(self, ship: Ship, column_width: int) -> RenderableType:
        line1 = ship.name.center(column_width)
        line2 = f"{ship.hull} ({ship.cost})".center(column_width)
        text = f"\n[b]{line1}[/b]\n{line2}"
        if ship.is_valid:
            mountings = self.get_sockets("Mountings", ship.mountings)
            compartments = self.get_sockets("Compartments", ship.compartments)
            modules = self.get_sockets("Modules", ship.modules)
            group = Group(text, mountings, compartments, modules)
        else:
            group = Group(text, self.get_sockets("Components", ship.components))

        return Padding(group, (0, 1))

    def print(self, with_title: bool, fleet: Fleet):
        column_width = min(COLUMN_WIDTH, self.console.width)
        number_of_columns = fleet.n_ships if fleet.n_ships > 2 else 3
        self.console.size = (min(number_of_columns * column_width, self.console.width), self.console.height)
        if with_title:
            self.console.print(Panel(Text(fleet.title.center(self.console.width), style="white"), style="orange"))

        if fleet.n_ships > 2:
            ships = [self.get_ship(ship, column_width) for ship in fleet.ships]
            self.console.print(Columns(ships, width=column_width, padding=(0, 0)))
            return

        ship_printer = ShipPrinter(self.console)
        for ship in fleet.ships:
            self.console.print()
            self.console.print(Text(ship.title.center(self.console.width), style="white"))
            ship_printer.print(False, ship)


def desired_console_width(num_of_columns: int) -> int:
    if num_of_columns < 3:
        return 3 * COLUMN_WIDTH
    width = num_of_columns * COLUMN_WIDTH
    if num_of_columns > 5:
        width = math.ceil(num_of_columns / 2) * COLUMN_WIDTH
    return width


def pad_str(string: str) -> str:
    padded_str = ""
    for line in string.splitlines():
        tokens = line.split(":", maxsplit=2)
        if len(tokens) != 2:
            padded_str += f"{line.strip()}\n"
            continue
        key, value = tokens[0], tokens[1]
        if not value:
            padded_str += f"\n[orange]{key.rjust(32 + len(key))}[/orange]\n"
            continue
        padded_key = key.strip().rjust(30)
        padded_str += f"[dim]{padded_key}[/dim]  {value.strip()}\n"
    return padded_str[:-1]


def print_any(printer: Printer, printable: Printable, mods: list[str], with_title: bool) -> None:
    printer.print(with_title, printable)
    printer.print_mods(mods)


def write_any(printable: Printable, num_of_columns: int, title: str, png_file: str):
    width = desired_console_width(num_of_columns)
    with open(os.devnull, "w") as file:
        console = Console(width=width, record=True, theme=nfc_theme, force_terminal=True, file=file)
        printable.print(console, False, [])
        svg_content = console.export_svg(title=title, clear=False)
        cairosvg.svg2png(bytestring=svg_content, write_to=png_file)
