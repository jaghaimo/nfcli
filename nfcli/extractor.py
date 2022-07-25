import json
import os
from typing import Dict

from unityparser import UnityDocument

from nfcli import load_path

TYPE_TO_NAME = {0: "mounts", 1: "compartments", 2: "modules"}


def add_socket(ship: Dict, socket: object):
    key = socket._key
    size = "x".join([str(x) for x in socket._size.values()])
    type = socket._type
    ship[TYPE_TO_NAME[type]][key] = size


def get_socket(file_id: str, all_entries: Dict[str, object]) -> Dict:
    transform = all_entries[file_id]
    game_object_id = str(transform.m_GameObject["fileID"])
    game_object = all_entries[game_object_id]
    attributes = ["_key", "_size", "_type"]
    for child in game_object.m_Component:
        socket_id = str(child["component"]["fileID"])
        socket = all_entries[socket_id]
        if all([hasattr(socket, attribute) for attribute in attributes]):
            return socket
    raise RuntimeError("Could not find a valid MonoBehaviour object")


def get_ship(entry: object, all_entries: Dict[str, object]) -> Dict:
    name = entry._className
    hull = entry._hullClassification
    ship = {"name": name, "hull": hull, "mounts": {}, "compartments": {}, "modules": {}}

    socket_root = str(entry._socketRoot["fileID"])
    socket_node = all_entries[socket_root]
    for child in socket_node.m_Children:
        socket = get_socket(str(child["fileID"]), all_entries)
        add_socket(ship, socket)

    return ship


def extract_ship_data(input: str):
    doc = UnityDocument.load_yaml(input)
    all_entries = {}
    for entry in doc.entries:
        all_entries[str(entry.anchor)] = entry

    entries = doc.filter(
        class_names=("MonoBehaviour",), attributes=("_className", "_hullClassification", "_socketRoot")
    )
    if len(entries) != 1:
        raise RuntimeError("Could not find a starting MonoBehaviour object")

    return get_ship(entries[0], all_entries)

def extract_from_prefabs():
    ships = {}
    prefabs_json = load_path("prefab/prefabs.json")
    prefabs = json.loads(prefabs_json)
    for prefab_file, namespace in prefabs.items():
        ship = extract_ship_data(os.path.join("prefab", prefab_file))
        ship_key = "/".join([namespace, ship["name"]])
        name_hull = " ".join([ship["name"], ship["hull"]])
        ship["name"] = name_hull
        del(ship["hull"])
        ships[ship_key] = ship

    with open("data/modded_ships.json", "w") as file:
        json.dump(ships, file, indent=4)
