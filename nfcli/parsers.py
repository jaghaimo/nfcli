import logging
import re
from typing import Dict, List, Optional, OrderedDict, Union

import xmltodict

from nfcli.database import db
from nfcli.models import Content, Fleet, Missile, Ship, Socket
from nfcli.printers import Printable
from nfcli.writers import Writeable


def list_to_str(list: List[str]) -> str:
    filtered_list = [element for element in list if element]
    return "\n".join(filtered_list)


def dict_to_str(dictionary: Dict[str, str]) -> str:
    as_list = [f"{key.rjust(27)}: {value}" if value else "" for key, value in dictionary.items()]
    return "\n".join(as_list)


def str_to_dict(string: Optional[str] = None) -> Dict[str, str]:
    if not string:
        return {}
    new_dict = {}
    for line in string.splitlines():
        tokens = line.split(":", maxsplit=2)
        if len(tokens) != 2:
            continue
        key, value = tokens[0], tokens[1]
        new_dict[sanitize(key)] = strip_tags(value)
    return new_dict


def sanitize(string: str) -> str:
    return string.replace("(", "").replace(")", "").strip()


def strip_tags(string: str) -> str:
    return re.sub("<[^<]+?>", "", string).strip()


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
        db.get_hull_data(hull),
    )
    socket_map = ship_data["SocketMap"]
    hull_socket = socket_map["HullSocket"] if socket_map else []
    for socket_data in hull_socket:
        socket = get_socket(socket_data)
        ship.add_socket(socket)

    return ship


def get_missile(missile_data: OrderedDict) -> Missile:
    return Missile(
        missile_data["Designation"],
        missile_data["Nickname"],
        strip_tags(missile_data["Description"]),
        strip_tags(missile_data["LongDescription"]),
        int(missile_data["Cost"]),
        missile_data["BodyKey"],
    )


def parse_mods(xml_data: str) -> List[str]:
    mods = []
    xmld = xmltodict.parse(xml_data, force_list=("unsignedLong"))
    _, entity = xmld.popitem()
    mod_deps_node = entity.get("ModDependencies") or {}
    mod_deps = mod_deps_node.get("unsignedLong") or []
    for mod_dep in mod_deps:
        mods.append(mod_dep)
    return mods


def parse_missile(xml_data: str) -> Missile:
    xmld = xmltodict.parse(xml_data)
    missile_template = xmld.get("MissileTemplate")
    return get_missile(missile_template)


def parse_ship(xml_data: str) -> Ship:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "HullSocket"))
    ship_data = xmld.get("Ship")
    return get_ship(ship_data)


def parse_fleet(xml_data: str) -> Fleet:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "Ship", "HullSocket", "MissileTemplate"))
    fleet_data = xmld.get("Fleet")
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    for idx, ship_data in enumerate(fleet_data["Ships"]["Ship"]):
        if idx > 9:
            logging.warn("Stopping after parsing 10 ships")
            break
        logging.debug(f"Parsing ship #{str(idx)}")
        ship = get_ship(ship_data)
        fleet.add_ship(ship)

    if "MissileTypes" not in fleet_data:
        return fleet

    for idx, missile_template in enumerate(fleet_data["MissileTypes"]["MissileTemplate"]):
        logging.debug(f"Parsing missile #{str(idx)}")
        missile = get_missile(missile_template)
        fleet.add_missile(missile)

    return fleet


def parse_any(filename: str, xml_data: str) -> Union[Printable, Writeable]:
    try:
        if filename.endswith("fleet"):
            return parse_fleet(xml_data)
        elif filename.endswith("ship"):
            return parse_ship(xml_data)
        elif filename.endswith("missile"):
            return parse_missile(xml_data)
    except Exception as exc:
        logging.error(exc.with_traceback())

    raise ValueError("Unrecognizable file format")
