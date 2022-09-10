import json
import logging
import os
import shutil
from abc import abstractproperty
from io import BytesIO
from typing import Callable, Dict, List, Optional
from urllib.request import urlopen
from zipfile import ZipFile

from fuzzywuzzy import process
from fuzzywuzzy.fuzz import partial_token_sort_ratio, token_sort_ratio

from nfcli import load_path, strip_tags

WIKI_DATA_URL = "https://gitlab.com/nebfltcom/data/-/archive/main/data-main.zip?path=wiki"
WIKI_DIR = "data/wiki"
WIKI_URL = "http://nebfltcom.wikidot.com/"


def list_to_str(list: List[str]) -> str:
    filtered_list = [element for element in list if element]
    return "\n".join(filtered_list)


def dict_to_str(dictionary: Dict[str, str]) -> str:
    as_list = [f"{key.rjust(27)}: {value}" if value else "" for key, value in dictionary.items()]
    return "\n".join(as_list)


def sanitize(string: str) -> str:
    return string.replace("(", "").replace(")", "").strip()


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


def update_wiki():
    zip_content = urlopen(WIKI_DATA_URL)
    zipfile = ZipFile(BytesIO(zip_content.read()))
    for member in zipfile.namelist():
        filename = os.path.basename(member)
        if not filename:
            continue
        logging.debug(f"Extracting {filename}")
        source = zipfile.open(member)
        target = open(os.path.join(WIKI_DIR, filename), "wb")
        with source, target:
            shutil.copyfileobj(source, target)


class Entity:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description.replace("\n\n", "\n")

    @property
    def header(self) -> str:
        return f"**{self.name}** [<{self.link}>]\n{self.description}\n```yaml\n"

    @property
    def footer(self) -> str:
        return "```"

    @abstractproperty
    def link(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def text(self) -> str:
        raise NotImplementedError

    def get_link(self, link: str) -> str:
        return WIKI_URL + link


class Hull(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["ClassName"] + " " + raw_data["HullClassification"], raw_data["LongDescription"])
        self.class_name: str = raw_data["ClassName"]
        self.size_class: str = raw_data["SizeClass"]
        self.point_cost: int = raw_data["PointCost"]
        self.mass: int = raw_data["Mass"]
        self.max_speed: int = raw_data["MaxSpeed"]
        self.linear_motor: int = raw_data["LinearMotor"]
        self.max_turn_speed: float = raw_data["MaxTurnSpeed"]
        self.angular_thrust: float = raw_data["AngularMotor"]
        self.base_integrity: int = raw_data["BaseIntegrity"]
        self.armour_thickness: int = raw_data["ArmorThickness"]
        self.component_damage_resistance: int = raw_data["MaxComponentDR"] * 100
        radar_data = [data["value"] for data in raw_data["SignatureData"]]
        self.max_radar: float = max(radar_data)
        self.min_radar: float = min(radar_data)
        self.vision_distance: int = raw_data["VisionDistance"]
        self.identity_work_value: int = raw_data["IdentityWorkValue"]
        self.hull_buffs: str = raw_data["EditorFormatHullBuffs"]

    @property
    def info(self) -> Dict[str, str]:
        info = {
            "Point Cost": str(self.point_cost),
            "Class Size": self.size_class,
            "Mass": f"{self.mass} tonnes",
        }
        info.update(str_to_dict(self.hull_buffs))
        return info

    @property
    def manoeuvrability(self) -> Dict[str, str]:
        linear_acceleration = 1000 * self.linear_motor / self.mass
        time_to_max_speed = self.max_speed / linear_acceleration
        return {
            "Manoeuvrability": "",
            "Linear Speed": f"{self.max_speed} m/s",
            "Linear Thrust": f"{self.linear_motor} MN",
            "Angular Speed": f"{self.max_turn_speed:.2f} deg/s",
            "Angular Thrust": f"{self.angular_thrust} MN",
            "Linear Acceleration": f"{linear_acceleration:.2f} m/s²",
            "Time to Linear Max Speed": f"{time_to_max_speed:.2f} s",
        }

    @property
    def durability(self) -> Dict[str, str]:
        return {
            "Durability": "",
            "Structural Integrity": str(self.base_integrity),
            "Armour Thickness": f"{self.armour_thickness} cm",
            "Component Damage Resistance": f"{self.component_damage_resistance}%",
        }

    @property
    def detectability(self) -> Dict[str, str]:
        return {
            "Detectability": "",
            "Radar Signature": f"{self.min_radar:.0f} m to {self.max_radar:.0f} m",
            "Visual Detection Distance": f"{self.vision_distance} m",
            "Identification Difficulty": str(self.identity_work_value),
        }

    @property
    def link(self) -> str:
        return self.get_link(f"hull:{self.class_name.lower()}")

    @property
    def text(self) -> str:
        info = dict_to_str(self.info)
        manoeuvrability = dict_to_str(self.manoeuvrability)
        durability = dict_to_str(self.durability)
        detectability = dict_to_str(self.detectability)
        return list_to_str([self.header, info, manoeuvrability, durability, detectability, self.footer])


class Component(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["ComponentName"], raw_data["LongDescription"])
        self.category: str = raw_data["Category"]
        self.type: str = raw_data["Type"]
        self.point_cost: int = raw_data["PointCost"]
        self.mass: int = raw_data["Mass"]
        self.size: Dict[str, int] = raw_data["Size"]
        self.scale_with_size: bool = raw_data["CanTile"]
        self.compounding_cost: bool = raw_data["CompoundingCost"]
        self.compounding_scale: int = raw_data["CompoundingMultiplier"]
        self.first_instance_free: bool = raw_data["FirstInstanceFree"]
        self.component_integrity: int = raw_data["MaxHealth"]
        self.reinforced: int = raw_data["Reinforced"]
        self.functioning_threshold: int = raw_data["FunctioningThreshold"]
        self.damage_resistance: int = raw_data["DamageResistance"]
        self.crew_data: Dict = raw_data["CrewOperatedComponentData"]
        ewar_data = {}
        if raw_data["TurretedEWarComponentData"]:
            ewar_data = raw_data["TurretedEWarComponentData"]
        elif raw_data["OmnidirectionalEWarComponentData"]:
            ewar_data = raw_data["OmnidirectionalEWarComponentData"]
        self.ewar_data: Dict = ewar_data
        sensor_data = {}
        if raw_data["SensorComponentData"]:
            sensor_data = raw_data["SensorComponentData"]
        self.sensor_data: Dict = sensor_data
        self.resources: str = raw_data["FormattedResources"]
        self.buffs: str = raw_data["FormattedBuffs"]

    @property
    def info(self) -> Dict[str, str]:
        info = {
            "Category": self.category,
            "Type": self.type,
        }
        if self.crew_data:
            info["Required Crew"] = str(self.crew_data["CrewRequired"]) if "CrewRequired" in self.crew_data else "none"
        info["Size"] = "x".join([str(x) for x in self.size.values()])
        info["Mass"] = f"{self.mass} tonnes"
        info.update(str_to_dict(self.resources))
        info.update(str_to_dict(self.buffs))
        return info

    @property
    def cost(self) -> Dict[str, str]:
        scale_with_size = " (scales with size)" if self.scale_with_size else ""
        compounding_cost = "Yes" if self.compounding_cost else "No"
        compounding_scale = f"(x{self.compounding_scale})" if self.compounding_scale > 1 else ""
        return {
            "Cost": "",
            "Point Cost": f"{self.point_cost}{scale_with_size}",
            "Compounding Cost": f"{compounding_cost} {compounding_scale}".strip(),
            "First Instance Free": "Yes" if self.first_instance_free else "No",
        }

    @property
    def durability(self) -> Dict[str, str]:
        return {
            "Durability": "",
            "Component Integrity": str(self.component_integrity),
            "Is Reinforced": "Yes" if self.reinforced else "No",
            "Functioning Threshold": str(self.functioning_threshold),
            "Damage Resistance": str(self.damage_resistance),
        }

    @property
    def ewar(self) -> Dict[str, str]:
        ewar = {}
        if self.ewar_data:
            ewar["EWar"] = ""
            ewar["Range"] = str(self.ewar_data["MaxRange"] / 1000) + " km"
            ewar["Radiated Power"] = str(self.ewar_data["RadiatedPower"]) + " kW"
            ewar["Gain"] = str(self.ewar_data["Gain"]) + " dB"
        return ewar

    @property
    def sensor(self) -> Dict[str, str]:
        sensor = {}
        if self.sensor_data:
            sensor["Sensors"] = ""
            sensor["Range"] = str(self.sensor_data["MaxRange"] / 1000) + " km"
            sensor["Radiated Power"] = str(self.sensor_data["RadiatedPower"]) + " W"
            sensor["Gain"] = str(self.sensor_data["Gain"]) + " dB"
        return sensor

    @property
    def link(self) -> str:
        name = self.name.lower().replace(" ", "-")
        return self.get_link(f"component:{name}")

    @property
    def text(self) -> str:
        info = dict_to_str(self.info)
        ewar = dict_to_str(self.ewar)
        sensor = dict_to_str(self.sensor)
        cost = dict_to_str(self.cost)
        durability = dict_to_str(self.durability)
        return list_to_str([self.header, info, ewar, sensor, cost, durability, self.footer])


class Munition(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["MunitionName"], "")
        self.type = raw_data["Type"]
        self.role = raw_data["Role"]
        self.point_cost = raw_data["PointCost"]
        self.volume = raw_data["StorageVolume"]
        self.division = raw_data["PointDivision"]
        self.set_from_description(raw_data["Description"])

    def set_from_description(self, description_and_details: str):
        description: List[str] = []
        details: List[str] = []
        for raw_line in description_and_details.splitlines():
            line = strip_tags(raw_line)
            if len(line) > 30:
                description.append(line)
            else:
                details.append(line)
        self.description = "\n".join(description)
        self.details = {"Details": ""}
        self.details.update(str_to_dict("\n".join(details)))

    @property
    def info(self) -> Dict[str, str]:
        unit = "units" if self.division > 1 else "unit"
        return {
            "Type": self.type,
            "Role": self.role,
            "Point Cost": f"{self.point_cost} points per {self.division} {unit}",
            "Storage Volume": f"{self.volume} m³",
        }

    @property
    def link(self) -> str:
        name = self.name.lower().replace(" ", "-")
        return self.get_link(f"munition:{name}")

    @property
    def text(self) -> str:
        info = dict_to_str(self.info)
        details = dict_to_str(self.details)
        return list_to_str([self.header, info, details, self.footer])


class Wiki:
    def __init__(self):
        self.entities = {}
        self._load()

    def get(self, key: str, scorer: Callable = token_sort_ratio, score_cutoff: int = 0) -> Entity:
        best_key = process.extractOne(key, self.entities.keys(), scorer=scorer, score_cutoff=score_cutoff)
        if not best_key:
            raise ValueError
        if best_key[1] > 51:
            return self.entities[best_key[0]]

        return self.get(key, partial_token_sort_ratio, 51)

    def _add_hull(self, hull: Dict) -> None:
        self._add(Hull(hull))

    def _add_component(self, component: Dict) -> None:
        self._add(Component(component))

    def _add_munition(self, munition: Dict) -> None:
        self._add(Munition(munition))

    def _add(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def _add_all(self, dirname: str, filenames: List[str], callback: Callable) -> None:
        for filename in filenames:
            content = self._read_json(dirname, filename)
            callback(content)

    def _process_aliases(self):
        aliases = self._read_json("data", "wiki.json")
        for source, target in aliases.items():
            entity = self.get(target)
            self.entities[source] = entity

    def _read_json(self, dirname: str, filename: str) -> Dict:
        content = load_path(os.path.join(dirname, filename))
        return json.loads(content)

    def _load(self) -> None:
        index = self._read_json(WIKI_DIR, "index.json")
        self._add_all(WIKI_DIR, index["hulls"], self._add_hull)
        self._add_all(WIKI_DIR, index["components"], self._add_component)
        self._add_all(WIKI_DIR, index["munitions"], self._add_munition)
        self._process_aliases()
