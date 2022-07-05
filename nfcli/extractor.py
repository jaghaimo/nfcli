import json
import logging
from typing import Dict

from nfcli.model import Fleet, Ship


def add_ship(info: Dict, ship: Ship):
    ship_info = {}
    ship_info["mountkeys"] = {}
    ship_info["compartmentkeys"] = {}
    ship_info["modulekeys"] = {}
    for key, socket in ship.sockets.items():
        if socket.name == "CR10 Antenna":
            ship_info["mountkeys"][socket.key] = {}
        elif socket.name == "Auxiliary Steering":
            ship_info["compartmentkeys"][socket.key] = {}
        elif socket.name == "Supplementary Radio Amplifiers":
            ship_info["modulekeys"][socket.key] = {}
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
