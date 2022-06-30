import logging
from typing import List, Optional, OrderedDict

import xmltodict

from nfcli.model import Content, Fleet, Ship, ShipFleetType, Socket


def clean_string(name: str, recursive: Optional[bool] = False) -> str:
    prefixes = ["Stock/"]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            if recursive:
                clean_string(name, recursive)

    return name


def get_content(content_data: OrderedDict) -> List[Content]:
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


def get_socket(socket_data: OrderedDict) -> Socket:
    content = []
    name = clean_string(socket_data["ComponentName"])
    if "ComponentData" in socket_data:
        content = get_content(socket_data["ComponentData"])

    return Socket(name, content)


def get_ship(ship_data: OrderedDict) -> Ship:
    ship = Ship(ship_data["Name"], ship_data["Cost"], clean_string(ship_data["HullType"]))
    for socket_data in ship_data["SocketMap"]["HullSocket"]:
        socket = get_socket(socket_data)
        ship.add_socket(socket)

    return ship


def parse_ship(xml_data: str) -> Ship:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData"))
    ship_data = xmld.get("Ship")
    return get_ship(ship_data)


def parse_fleet(xml_data: str) -> Fleet:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "Ship"))
    fleet_data = xmld.get("Fleet")
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    for idx, ship_data in enumerate(fleet_data["Ships"]["Ship"]):
        logging.info(f"Parsing ship #{str(idx)}")
        ship = get_ship(ship_data)
        fleet.add_ship(ship)
        if idx == 9:
            logging.warn("Stopping after parsing 10 ships")
            break

    return fleet


def parse_any(filename: str, xml_data: str) -> ShipFleetType:
    if filename.endswith("fleet"):
        return parse_fleet(xml_data)
    elif filename.endswith("ship"):
        return parse_ship(xml_data)

    raise ValueError("Unrecognizable file format")
