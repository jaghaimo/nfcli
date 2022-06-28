import logging
from typing import List, Optional, OrderedDict

import xmltodict

from nfcli import load_path
from nfcli.model import Content, Fleet, Ship, Socket


def clean_string(name: str, recursive: Optional[bool] = False) -> str:
    prefixes = ["Stock/"]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
            if recursive:
                clean_string(name, recursive)

    return name

def parse_content(content_data: OrderedDict) -> List[Content]:
    content = []
    all_loads = []
    for key in ["MissileLoad", "Load"]:
        if key in content_data and content_data[key]:
            all_loads += content_data[key]["MagSaveData"]

    for load in all_loads:
        name = clean_string(load["MunitionKey"])
        quantity = load["Quantity"]
        content.append(Content(name, quantity))

    return content

def parse_socket(socket_data: OrderedDict) -> Socket:
    content = []
    name = clean_string(socket_data["ComponentName"])
    if "ComponentData" in socket_data:
        content = parse_content(socket_data["ComponentData"])

    return Socket(name, content)

def parse_ship(ship_data: OrderedDict) -> Ship:
    ship = Ship(ship_data["Name"], ship_data["Cost"], clean_string(ship_data["HullType"]))
    for socket_data in ship_data["SocketMap"]["HullSocket"]:
        socket = parse_socket(socket_data)
        ship.add_socket(socket)

    return ship

def parse_input(input_fleet: str) -> Fleet:
    xml_data = load_path(input_fleet)
    xmld = xmltodict.parse(xml_data, force_list="MagSaveData")
    fleet_data = xmld.get("Fleet")
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    for ship_data in fleet_data["Ships"]["Ship"]:
        ship = parse_ship(ship_data)
        fleet.add_ship(ship)

    return fleet
