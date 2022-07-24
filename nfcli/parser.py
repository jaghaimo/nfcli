import logging
from typing import List, OrderedDict

import xmltodict

from nfcli.database import db
from nfcli.model import Content, Fleet, Ship, ShipFleetType, Socket


def get_content(content_data: OrderedDict) -> List[Content]:
    content = []
    all_loads = []
    for key in ["MissileLoad", "Load"]:
        if key in content_data and content_data[key]:
            all_loads += content_data[key]["MagSaveData"]

    for load in all_loads:
        content.append(Content(load["MunitionKey"], load["Quantity"]))

    return content


def get_socket(socket_data: OrderedDict) -> Socket:
    name = socket_data["ComponentName"]
    content = []
    if "ComponentData" in socket_data:
        content = get_content(socket_data["ComponentData"])
    return Socket(socket_data["Key"], name, content, db.get_component_tag(name))


def get_ship(ship_data: OrderedDict) -> Ship:
    hull = ship_data["HullType"]
    ship = Ship(
        ship_data["Name"],
        ship_data["Cost"],
        ship_data["Number"],
        ship_data["SymbolOption"],
        hull,
        db.get_ship_data(hull),
    )
    socket_map = ship_data["SocketMap"]
    hull_socket = socket_map["HullSocket"] if socket_map else []
    for socket_data in hull_socket:
        socket = get_socket(socket_data)
        ship.add_socket(socket)

    return ship


def parse_mods(xml_data: str) -> List[str]:
    mods = []
    xmld = xmltodict.parse(xml_data, force_list=("unsignedLong"))
    _, entity = xmld.popitem()
    mod_deps_node = entity.get("ModDependencies") or {}
    mod_deps = mod_deps_node.get("unsignedLong") or []
    for mod_dep in mod_deps:
        mods.append(mod_dep)
    return mods


def parse_ship(xml_data: str) -> Ship:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "HullSocket"))
    ship_data = xmld.get("Ship")
    return get_ship(ship_data)


def parse_fleet(xml_data: str) -> Fleet:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "Ship", "HullSocket"))
    fleet_data = xmld.get("Fleet")
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    for idx, ship_data in enumerate(fleet_data["Ships"]["Ship"]):
        if idx > 9:
            logging.warn("Stopping after parsing 10 ships")
            break
        logging.info(f"Parsing ship #{str(idx)}")
        ship = get_ship(ship_data)
        fleet.add_ship(ship)

    return fleet


def parse_any(filename: str, xml_data: str) -> ShipFleetType:
    try:
        if filename.endswith("fleet"):
            return parse_fleet(xml_data)
        elif filename.endswith("ship"):
            return parse_ship(xml_data)
    except Exception as exc:
        logging.error(exc.with_traceback())

    raise ValueError("Unrecognizable file format")
