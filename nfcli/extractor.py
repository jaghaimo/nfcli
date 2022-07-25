import json
import logging
import os
from glob import glob
from posixpath import basename
from typing import Dict

from ruamel.yaml import YAML

from nfcli import load_path
from nfcli.model import Fleet, Ship
from nfcli.parser import parse_fleet


def add_ship(info: Dict, ship: Ship, socket_data: Dict):
    ship_info = {"name": ship.name}
    ship_info["mounts"] = {}
    ship_info["compartments"] = {}
    ship_info["modules"] = {}
    for key, socket in ship.sockets.items():
        socket_size = socket_data.get(socket.key) if socket.key in socket_data else "?x?x?"
        if socket.name == "CR10 Antenna":
            ship_info["mounts"][socket.key] = socket_size
        elif socket.name == "Auxiliary Steering":
            ship_info["compartments"][socket.key] = socket_size
        elif socket.name == "Supplementary Radio Amplifiers":
            ship_info["modules"][socket.key] = socket_size
        else:
            logging.warn(f"Unrecognized socket {key} which contains {socket.name}")
    info[ship._hull] = ship_info


def get_socket_data(input: str) -> Dict:
    path = os.path.join("prefab", basename(input)[:-6], "*.json")
    socket_data = {}
    for filename in glob(path):
        raw_data = load_path(filename)
        hull_data = json.loads(raw_data)
        key = hull_data["_key"]
        value = hull_data["_size"]
        socket_data[key] = "x".join([str(x) for x in value.values()])
    return socket_data


def extract_slots(input: str, output: str):
    xml_data = load_path(input)
    fleet = parse_fleet(xml_data)
    if not isinstance(fleet, Fleet):
        raise ValueError("Not a Fleet type")
    info = {}
    socket_data = get_socket_data(input)
    for ship in fleet.ships:
        add_ship(info, ship, socket_data)
    with open(output, "w") as file:
        json.dump(info, file, indent=4)
