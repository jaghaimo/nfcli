import logging
from collections import Counter

import xmltodict

from nfcli import clean_text
from nfcli.data import Components, Hulls, Munitions, Tags
from nfcli.models import Content, Craft, Fleet, Missile, Ship, Socket
from nfcli.printers import Printable


def get_content(content_data: dict) -> list[Content]:
    all_munitions = []
    for key in ["MissileLoad", "Load"]:
        if content_data.get(key):
            all_munitions += [
                Content(Munitions.get_name_or_key(load["MunitionKey"]), load["Quantity"])
                for load in content_data[key]["MagSaveData"]
            ]

    all_crafts = []
    if content_data.get("StoredCraft"):
        all_hangar_loads = Counter(
            craft["CraftTemplateKey"] for craft in content_data["StoredCraft"]["SavedStoredCraft"]
        )
        all_crafts = [Content(craft, quantity) for craft, quantity in all_hangar_loads.items()]

    return all_munitions + all_crafts


def get_socket(socket_data: dict) -> Socket:
    name = socket_data["ComponentName"]
    content = []
    if "ComponentData" in socket_data:
        content = get_content(socket_data["ComponentData"])
    return Socket(socket_data["Key"], Components.get_name_or_key(name), content, Tags.get(name))


def get_ship(ship_data: dict) -> Ship:
    hull = ship_data["HullType"]
    ship = Ship(
        ship_data["Name"],
        ship_data["Cost"],
        ship_data["Number"],
        ship_data["SymbolOption"],
        hull,
        Hulls.get_data(hull),
    )
    socket_map = ship_data["SocketMap"]
    hull_socket = socket_map["HullSocket"] if socket_map else []
    for socket_data in hull_socket:
        socket = get_socket(socket_data)
        ship.add_socket(socket)

    return ship


def get_missile(missile_data: dict) -> Missile:
    return Missile(
        missile_data["Designation"],
        missile_data["Nickname"],
        clean_text(missile_data["Description"]),
        clean_text(missile_data["LongDescription"]),
        int(missile_data["Cost"]),
        missile_data["BodyKey"],
    )


def get_craft(craft_data: dict) -> Craft:
    return Craft(
        craft_data["DesignationSuffix"],
        craft_data["Nickname"],
        clean_text(craft_data["LongDescription"]),
        int(craft_data["Cost"]),
        craft_data["FrameKey"],
    )


def parse_mods(xml_data: str) -> list[str]:
    xmld = xmltodict.parse(xml_data, force_list=("unsignedLong"))
    _, entity = xmld.popitem()
    mod_deps_node = entity.get("ModDependencies") or {}
    mod_deps = mod_deps_node.get("unsignedLong") or []
    return list(mod_deps)


def parse_craft(xml_data: str) -> Craft:
    xmld = xmltodict.parse(xml_data)
    craft_template: dict = xmld.get("CraftTemplate")  # type: ignore
    return get_craft(craft_template)


def parse_missile(xml_data: str) -> Missile:
    xmld = xmltodict.parse(xml_data)
    missile_template: dict = xmld.get("MissileTemplate")  # type: ignore
    return get_missile(missile_template)


def parse_ship(xml_data: str) -> Ship:
    xmld = xmltodict.parse(xml_data, force_list=("MagSaveData", "HullSocket", "SavedStoredCraft"))
    ship_data: dict = xmld.get("Ship")  # type: ignore
    return get_ship(ship_data)


def parse_fleet(xml_data: str) -> Fleet:
    xmld = xmltodict.parse(
        xml_data, force_list=("MagSaveData", "Ship", "HullSocket", "MissileTemplate", "SavedStoredCraft")
    )
    fleet_data: dict = xmld.get("Fleet")  # type: ignore
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    logging.debug("Parsing ships.")
    for idx, ship_data in enumerate(fleet_data["Ships"]["Ship"]):
        logging.debug(f"Parsing ship #{idx!s}")
        ship = get_ship(ship_data)
        fleet.add_ship(ship)

    missile_types = fleet_data.get("MissileTypes", {})
    if not missile_types:
        return fleet
    missile_templates = missile_types.get("MissileTemplate", [])
    if not missile_templates:
        return fleet

    logging.debug("Parsing missiles.")
    for idx, missile_template in enumerate(missile_templates):
        logging.debug(f"Parsing missile #{idx!s}")
        missile = get_missile(missile_template)
        fleet.add_missile(missile)

    return fleet


def parse_any(filename: str, xml_data: str) -> Printable:
    if filename.endswith("fleet"):
        return parse_fleet(xml_data)
    elif filename.endswith("ship"):
        return parse_ship(xml_data)
    elif filename.endswith("missile"):
        return parse_missile(xml_data)
    elif filename.endswith("craft"):
        return parse_craft(xml_data)

    raise ValueError("Unrecognizable file format")
