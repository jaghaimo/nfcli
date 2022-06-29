from typing import Set

from nfcli import load_path


class Database:
    def __init__(self) -> None:
        self.mountings = set()
        self.compartments = set()
        self.modules = set()

    def is_mounting(self, name: str) -> bool:
        return name in self.mountings

    def is_compartment(self, name: str) -> bool:
        return name in self.compartments

    def is_module(self, name: str) -> bool:
        return name in self.modules

    def is_invalid(self, name: str) -> bool:
        checks = (
            int(self.is_mounting(name)) + int(self.is_compartment(name)) + int(self.is_module(name))
        )
        return checks != 1


db = Database()


def add_from_path(path: str, set_to_add: Set):
    characters = load_path(path)
    lines = characters.split("\n")
    for line in lines:
        if line.startswith("#"):
            continue
        set_to_add.add(line)


def init_database():
    add_from_path("data/mountings.txt", db.mountings)
    add_from_path("data/compartments.txt", db.compartments)
    add_from_path("data/modules.txt", db.modules)
