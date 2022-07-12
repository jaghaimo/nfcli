from __future__ import annotations

import logging
import math
from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, List, Optional, Tuple, Type

from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.tree import Tree

from nfcli import COLUMN_WIDTH, STACK_COLUMNS, nfc_theme

if TYPE_CHECKING:
    from nfcli.model import Component, Fleet, Ship, ShipFleetType


class Printable:
    @abstractproperty
    def title(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def print(self, printer: Printer):
        raise NotImplementedError


class Printer(ABC):
    @abstractmethod
    def print(self, printable: Printable):
        raise NotImplementedError


class FleetPrinter(Printer):
    def __init__(self, column_width: int, console: Console, no_title: Optional[bool] = False):
        self.column_width = column_width
        self.console = console
        self.no_title = no_title

    def print(self, fleet: "Fleet"):
        if not self.no_title:
            self.console.print(Panel(Text(fleet.title.center(self.console.width), style="white"), style="orange"))

    def print_mods(self, mods: List[str]):
        if not mods:
            return

        self.console.print(self.get_mods(mods))

    @classmethod
    def get_mods(self, mods: List[str], begin_quote: Optional[str] = "", end_quote: Optional[str] = "") -> str:
        if not mods:
            return ""
        mods_text = "\nMods required:"
        for mod in mods:
            mods_text += f"\n- {begin_quote}https://steamcommunity.com/sharedfiles/filedetails/?id={mod}{end_quote}"
        return mods_text

    def add_components(self, tree: Tree, component: "Component"):
        for content in component.contents:
            tree.add(Text(f"{content.name} x{content.quantity}", overflow="ignore"), style="i d")

    def get_sockets(self, title: str, components: List["Component"], color: Optional[str] = "white") -> Group:
        elements = [Rule(Text(f"{title}", style="orange"), style="orange")]
        for component in components:
            slot_number = component.slot_number
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


class ColumnPrinter(FleetPrinter):
    def get_ship(self, ship: "Ship") -> RenderableType:
        line1 = ship.name.center(self.column_width)
        line2 = f"{ship.hull} ({ship.cost})".center(self.column_width)
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
        super().print(fleet)
        ships = [self.get_ship(ship) for ship in fleet.ships]
        self.console.print(Columns(ships, width=self.column_width, padding=(0, 0)))


class StackPrinter(FleetPrinter):
    def get_ship(self, ship: "Ship", no_ship_title: Optional[bool] = False) -> RenderableType:
        props = ["mountings", "compartments", "modules"]
        sockets = [Padding(self.get_sockets(prop.title(), getattr(ship, prop)), (0, 1)) for prop in props]
        if not no_ship_title:
            self.console.print("\n" + ship.title.center(self.console.width), highlight=False)
        return Columns(sockets, width=self.column_width, padding=(0, 0))

    def print(self, fleet: "Fleet"):
        super().print(fleet)
        for ship in fleet.valid_ships:
            self.console.print(self.get_ship(ship))


def determine_printer(num_of_ships: int, is_valid: bool) -> Tuple[int, Type[FleetPrinter]]:
    if num_of_ships < 4 and is_valid:
        return (STACK_COLUMNS * COLUMN_WIDTH, StackPrinter)

    width = num_of_ships * COLUMN_WIDTH
    if num_of_ships > 5:
        width = math.ceil(num_of_ships / 2) * COLUMN_WIDTH

    return (width, ColumnPrinter)


def fleet_printer_factory(printer_style: str, fleet: "Fleet"):
    console = Console(theme=nfc_theme)
    if printer_style == "stack":
        logging.debug("Returning StackPrinter")
        console.size = (min(STACK_COLUMNS * COLUMN_WIDTH, console.width), console.height)
        column_width = int(console.width / STACK_COLUMNS)
        return StackPrinter(column_width, console)

    num_of_ships = fleet.n_ships
    if printer_style == "column" or not fleet.is_valid:
        logging.debug("Returning ColumnPrinter")
        column_width = min(COLUMN_WIDTH, console.width)
        console.width = min(num_of_ships * column_width, console.width)
        return ColumnPrinter(column_width, console)
    elif printer_style == "auto":
        printer_style = "stack" if console.width < num_of_ships * COLUMN_WIDTH else "column"
        printer_style = printer_style if num_of_ships > 3 else "stack"
        return fleet_printer_factory(printer_style, fleet)

    logging.warn("Unknown printer requested, returning 'auto'")
    return fleet_printer_factory("auto", fleet)


def printer_factory(printer_style: str, entity: "ShipFleetType"):
    if entity.__class__.__name__ == "Fleet":
        return fleet_printer_factory(printer_style, entity)

    return fleet_printer_factory("stack", 1)
