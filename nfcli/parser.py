from typing import List, OrderedDict

import xmltodict

from nfcli.model import Fleet, Ship, Socket


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def parse_content(content_data: OrderedDict) -> List[str]:
    content = []
    all_loads = []
    for key in ["MissileLoad", "Load"]:
        if key in content_data:
            all_loads += content_data[key]["MagSaveData"]

    for load in all_loads:
        name = load["MunitionKey"]
        quantity = load["Quantity"]
        content.append(f"{name} x {quantity}")

    return content

def parse_socket(socket_data: OrderedDict) -> Socket:
    content = []
    if "ComponentData" in socket_data:
        content = parse_content(socket_data["ComponentData"])

    return Socket(socket_data["ComponentName"], content)

def parse_ship(ship_data: OrderedDict) -> Ship:
    ship = Ship(ship_data["Name"], ship_data["Cost"], ship_data["HullType"])
    for socket_data in ship_data["SocketMap"]["HullSocket"]:
        socket = parse_socket(socket_data)
        ship.add_socket(socket)

    return ship

def parse_input(input_fleet: str) -> Fleet:
    xml_data = load_path(input_fleet)
    xmld = xmltodict.parse(xml_data)
    fleet_data = xmld.get("Fleet")
    fleet = Fleet(fleet_data["Name"], fleet_data["TotalPoints"], fleet_data["FactionKey"])
    for ship_data in fleet_data["Ships"]["Ship"]:
        ship = parse_ship(ship_data)
        fleet.add_ship(ship)

    return fleet
