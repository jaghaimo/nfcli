from __future__ import annotations

import math
from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, List

from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS

if TYPE_CHECKING:
    from nfcli.models import Component, Fleet, Ship


class Printable:
    @abstractproperty
    def title(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def print(self, console: Console, mods: List[str]):
        raise NotImplementedError


class Printer(ABC):
    def __init__(self, console: Console):
        self.console = console

    @abstractmethod
    def print(self, printable: Printable):
        raise NotImplementedError

    @classmethod
    def get_mods(cls, mods: List[str], begin_quote: str = "", end_quote: str = "") -> str:
        if not mods:
            return ""
        mods_text = "\nMods required:"
        for mod in mods:
            mods_text += f"\n- {begin_quote}https://steamcommunity.com/sharedfiles/filedetails/?id={mod}{end_quote}"
        return mods_text

    def print_mods(self, mods: List[str]):
        if not mods:
            return
        self.console.print(self.get_mods(mods))


class ShipPrinter(Printer):
    def __init__(self, console: Console):
        super().__init__(console)

    def add_components(self, tree: Tree, component: "Component"):
        for content in component.contents:
            tree.add(Text(f"{content.name} x{content.quantity}", overflow="ignore"), style="i d")

    def get_sockets(self, title: str, components: List["Component"], color: str = "white") -> Group:
        elements: List[RenderableType] = [Rule(Text(f"{title}", style="orange"), style="orange")]
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

    def get_ship(self, ship: "Ship", column_width: int) -> RenderableType:
        props = ["mountings", "compartments", "modules"]
        sockets = [Padding(self.get_sockets(prop.title(), getattr(ship, prop)), (0, 1)) for prop in props]
        self.console.print("\n" + ship.title.center(self.console.width), highlight=False)
        return Columns(sockets, width=column_width, padding=(0, 0))

    def print(self, ship: "Ship"):
        self.console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, self.console.width), self.console.height)
        column_width = int(self.console.width / STACK_COLUMNS)
        self.console.print(self.get_ship(ship, column_width))


class FleetPrinter(ShipPrinter):
    def get_ship(self, ship: "Ship", column_width: int) -> RenderableType:
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

    def print(self, fleet: "Fleet"):
        column_width = min(COLUMN_WIDTH, self.console.width)
        self.console.width = min(fleet.n_ships * column_width, self.console.width)
        self.console.print(Panel(Text(fleet.title.center(self.console.width), style="white"), style="orange"))
        ships = [self.get_ship(ship, column_width) for ship in fleet.ships]
        self.console.print(Columns(ships, width=column_width, padding=(0, 0)))


def determine_width(num_of_columns: int) -> int:
    width = num_of_columns * COLUMN_WIDTH
    if num_of_columns > 5:
        width = math.ceil(num_of_columns / 2) * COLUMN_WIDTH
    return width


def print_any(printer: Printer, printable: Printable, mods: List[str]) -> None:
    printer.print(printable)
    printer.print_mods(mods)


# def fleet_printer_factory(printer_style: str, fleet: Optional["Fleet"] = None) -> ShipPrinter:
#     console = Console(theme=nfc_theme)
#     if printer_style == "stack" or fleet is None:
#         logging.debug("Returning StackPrinter")
#         console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, console.width), console.height)
#         column_width = int(console.width / STACK_COLUMNS)
#         return StackPrinter(column_width, console)

#     num_of_ships = fleet.n_ships
#     if printer_style == "column" or not fleet.is_valid:
#         logging.debug("Returning ColumnPrinter")
#         column_width = min(COLUMN_WIDTH, console.width)
#         console.width = min(num_of_ships * column_width, console.width)
#         return FleetPrinter(column_width, console)
#     elif printer_style == "auto":
#         logging.debug("Determining printer based on fleet and console size")
#         printer_style = "stack" if console.width < num_of_ships * COLUMN_WIDTH else "column"
#         printer_style = printer_style if num_of_ships > 3 else "stack"
#         return fleet_printer_factory(printer_style, fleet)

#     logging.warn("Unknown printer requested, returning 'auto'")
#     return fleet_printer_factory("auto", fleet)
