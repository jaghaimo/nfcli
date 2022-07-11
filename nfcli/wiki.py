import json
import logging
import os
import shutil
from abc import abstractproperty
from io import BytesIO
from typing import Callable, Dict, List
from urllib.request import urlopen
from zipfile import ZipFile

from fuzzywuzzy import process
from fuzzywuzzy.fuzz import token_sort_ratio

from nfcli import load_path

WIKI_DIR = "wiki"
WIKI_DATA_URL = "https://gitlab.com/nebfltcom/data/-/archive/main/data-main.zip?path=wiki"


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
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractproperty
    def text(self) -> str:
        raise NotImplementedError


class Hull(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["ClassName"])
        self.cost = raw_data["PointCost"]
        self.hull = raw_data["HullClassification"]

    @property
    def text(self) -> str:
        return f"{self.name} is a {self.cost} points {self.hull}."


class Component(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["ComponentName"])
        self.cost = raw_data["PointCost"]
        self.type = raw_data["Type"]

    @property
    def text(self) -> str:
        return f"{self.name} is a {self.cost} points {self.type} component."


class Munition(Entity):
    def __init__(self, raw_data: Dict) -> None:
        super().__init__(raw_data["MunitionName"])
        self.cost = raw_data["PointCost"]
        self.division = raw_data["PointDivision"]

    @property
    def text(self) -> str:
        return f"{self.name} costs {self.cost} points per {self.division}."


class Wiki:
    def __init__(self):
        self.entities = {}
        self._load()

    def get(self, key: str) -> Entity:
        best_key = process.extractOne(key, self.entities.keys(), scorer=token_sort_ratio)
        if not best_key:
            raise ValueError
        return self.entities[best_key[0]]

    def _add_hull(self, hull: Dict) -> None:
        self._add(Hull(hull))

    def _add_component(self, component: Dict) -> None:
        self._add(Component(component))

    def _add_munition(self, munition: Dict) -> None:
        self._add(Munition(munition))

    def _add(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def _add_all(self, filenames: List[str], callback: Callable) -> None:
        for filename in filenames:
            content = self._read_json(filename)
            callback(content)

    def _read_json(self, filename: str) -> Dict:
        content = load_path(os.path.join(WIKI_DIR, filename))
        return json.loads(content)

    def _load(self) -> None:
        index = self._read_json("index.json")
        self._add_all(index["hulls"], self._add_hull)
        self._add_all(index["components"], self._add_component)
        self._add_all(index["munitions"], self._add_munition)
