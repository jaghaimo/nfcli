import json
import logging
from typing import Dict

from nfcli import load_path
from nfcli.model import Fleet, Ship


def add_ship(info: Dict, ship: Ship):
    ship_info = {}
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


def get_sockets(ship_data: Dict) -> Dict:
    sockets = {}
    for key, value in ship_data.items():
        sockets[key] = "x".join([str(x) for x in value.get("size")])
    return sockets


def convert_nfm_data():
    """This is a one off to convert Nebulous Fleet Manager android app data."""
    convert_ships()
    convert_components()

def convert_ships():
    stock_ships = load_path("data/stock_ships_old.json")
    ships = json.loads(stock_ships)
    new_data = {}
    for ship_name, ship_data in ships.items():
        data = {
            "name": ship_name,
            "mounts": get_sockets(ship_data.get("mountkeys")),
            "compartments": get_sockets(ship_data.get("compartmentkeys")),
            "modules": get_sockets(ship_data.get("modulekeys")),
        }
        new_data[ship_name] = data
    with open("data/stock_ships.json", "w") as file:
        json.dump(new_data, file, indent=4)


def convert_components():
    stock_components = load_path("data/stock_components_old.json")
    components = json.loads(stock_components)
    new_data = {}
    for component_name, component_data in components.items():
        new_data[component_name] = component_data.get("category")
    with open("data/stock_components.json", "w") as file:
        json.dump(new_data, file, indent=4)
