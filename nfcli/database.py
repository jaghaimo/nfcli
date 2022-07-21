import json
import logging
from glob import glob
from typing import Dict

KEY_SLOT = "slot"

SOCKET_MOUNT = "mount"
SOCKET_COMPARTMENT = "compartment"
SOCKET_MODULE = "module"
SOCKET_AMMO = "ammo"
SOCKET_UNKNOWN = "unknown"


class Database:
    def __init__(self) -> None:
        self.components = self.load_all("data/*_components.json")
        self.ships = self.load_all("data/*_ships.json")

    def load_all(self, glob_path: str) -> Dict:
        loaded = {}
        for path in glob(glob_path):
            logging.debug(f"Reading {path}")
            loaded.update(self.load_json(path))
        return loaded

    def load_json(self, path: str) -> Dict:
        try:
            f = open(path, "r")
        except EnvironmentError:
            return {}
        else:
            return json.load(f)

    def get_component_data(self, socket: str) -> Dict:
        if socket in self.components:
            return self.components.get(socket)
        return {}

    def get_ship_data(self, hull: str) -> Dict:
        if hull in self.ships:
            return self.ships.get(hull)
        return {}


db = Database()
