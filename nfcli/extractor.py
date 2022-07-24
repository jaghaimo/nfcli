import json
import logging
from typing import Dict

from nfcli.model import Fleet, Ship


def add_ship(info: Dict, ship: Ship):
    ship_info = {"name": ship.name}
    ship_info["mounts"] = {}
    ship_info["compartments"] = {}
    ship_info["modules"] = {}
    for key, socket in ship.sockets.items():
        if socket.name == "CR10 Antenna":
            ship_info["mounts"][socket.key] = "?x?x?"
        elif socket.name == "Auxiliary Steering":
            ship_info["compartments"][socket.key] = "?x?x?"
        elif socket.name == "Supplementary Radio Amplifiers":
            ship_info["modules"][socket.key] = "?x?x?"
        else:
            logging.warn(f"Unrecognized socket {key} which contains {socket.name}")
    info[ship._hull] = ship_info


def extract_slots(output: str, fleet: Fleet):
    if not isinstance(fleet, Fleet):
        raise ValueError("Not a Fleet type")
    info = {}
    for ship in fleet.ships:
        add_ship(info, ship)
    with open(output, "w") as file:
        json.dump(info, file, indent=4)
