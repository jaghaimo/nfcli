import json
from typing import Dict

KEY_SLOT = "slot"

SOCKET_MOUNT = "mount"
SOCKET_COMPARTMENT = "compartment"
SOCKET_MODULE = "module"
SOCKET_AMMO = "ammo"
SOCKET_UNKNOWN = "unknown"


class Database:
    def __init__(self) -> None:
        # NEBFLTCOM Data (unused)
        self.components = dict()
        self.ships = dict()
        # Nebulous Fleet Manager
        self.component_data = self.load_json("data/component_data.json")
        self.ship_data = self.load_json("data/ship_data.json")

    def find_socket_attr(self, ship_data: Dict, key: str, attr: str) -> str:
        sockets = [
            ship_data.get(socket_type).get(key)
            for socket_type in ["mountkeys", "compartmentkeys", "modulekeys"]
            for sockets in ship_data.get(socket_type)
            if key in sockets
        ]

        if len(sockets) == 1:
            return sockets[0].get(attr)

        return SOCKET_UNKNOWN.title()

    def load_json(self, path_to_file: str) -> Dict:
        with open(path_to_file, "r") as f:
            return json.load(f)

    def get_name(self, name: str) -> str:
        return name.split("/")[-1]

    def get_socket_attr(self, hull: str, key: str, attr: str) -> str:
        try:
            ship_data = self.ship_data.get(hull)
            return self.find_socket_attr(ship_data, key, attr)
        except AttributeError:
            return SOCKET_UNKNOWN

    def get_slot(self, name: str) -> str:
        try:
            return self.component_data.get(name).get(KEY_SLOT)
        except AttributeError:
            return SOCKET_UNKNOWN

    def is_mounting(self, name: str) -> bool:
        return self.get_slot(name) == SOCKET_MOUNT

    def is_compartment(self, name: str) -> bool:
        return self.get_slot(name) == SOCKET_COMPARTMENT

    def is_module(self, name: str) -> bool:
        return self.get_slot(name) == SOCKET_MODULE

    def is_ammo(self, name: str) -> bool:
        return self.get_slot(name) == SOCKET_AMMO

    def is_invalid(self, name: str) -> bool:
        checks = (
            int(self.is_mounting(name)) + int(self.is_compartment(name)) + int(self.is_module(name))
        )
        return checks != 1


db = Database()
