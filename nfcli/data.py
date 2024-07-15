"""Handles static content in `data/` folder."""

import json
import logging
from glob import glob
from typing import Any

TAGS_FILE = "data/tags.json"
COMPONENTS_FILE = "data/components.json"
MUNITIONS_FILE = "data/munitions.json"


def load_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except OSError:
        logging.warn(f"Failed to load {path}")
    return {}


class _Hulls:
    def __init__(self) -> None:
        self.hulls: dict[str, dict] = {}
        self._load_hulls()

    def _load_hulls(self):
        for file in glob("data/hulls/*.json"):
            hull = load_json(file)
            key = hull["key"]
            self.hulls[key] = hull

    def get_data(self, hull: str) -> dict:
        return self.hulls.get(hull, {})


class _Tags:
    def __init__(self) -> None:
        self.tags: dict[str, Any] = load_json(TAGS_FILE)

    def get(self, name: str) -> str | None:
        if name in self.tags:
            return self.tags.get(name)
        return None

    def merge(self, new_dict: dict[str, Any]):
        current_keys = self.tags.keys()
        new_keys = new_dict.keys()
        self.remove_keys(current_keys - new_keys)
        new_dict.update(self.tags)
        self.tags = new_dict

    def save(self):
        with open(TAGS_FILE, "w") as file:
            json.dump(self.tags, file, indent=4, sort_keys=True)

    def remove_keys(self, removed_keys: list[str] | set[str]):
        if not removed_keys:
            return
        logging.info(f"Removing old entries: {removed_keys}")
        for key in removed_keys:
            self.tags.pop(key)


class _Components:
    def __init__(self) -> None:
        self.components = load_json(COMPONENTS_FILE).get("Components")

    def get_name(self, key: str) -> str | None:
        if self.components is None:
            return None
        for component in self.components:
            if component.get("Key") == key:
                return component.get("Name")
        return None

    def get_name_or_key(self, key: str) -> str:
        name = self.get_name(key)
        if name is None:
            return key
        else:
            return name


class _Munitions:
    def __init__(self) -> None:
        self.munitions = load_json(MUNITIONS_FILE).get("Munitions")

    def get_name(self, key: str) -> str | None:
        if self.munitions is None:
            return None
        for munition in self.munitions:
            if munition.get("Key") == key:
                return munition.get("Name")
        return None

    def get_name_or_key(self, key: str) -> str:
        name = self.get_name(key)
        if name is None:
            return key
        else:
            return name


Hulls = _Hulls()
Tags = _Tags()
Components = _Components()
Munitions = _Munitions()
