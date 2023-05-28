"""Handles static content in `data/` folder."""

import json
import logging
from glob import glob

TAGS_FILE = "data/tags.json"


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
        if hull in self.hulls:
            return self.hulls.get(hull)
        return {}


class _Tags:
    def __init__(self) -> None:
        self.tags = load_json(TAGS_FILE)

    def get(self, name: str) -> str | None:
        if name in self.tags:
            return self.tags.get(name)
        return None

    def merge(self, new_dict: dict):
        current_keys = self.tags.keys()
        new_keys = new_dict.keys()
        self.remove_keys(current_keys - new_keys)
        new_dict.update(self.tags)
        self.tags = new_dict

    def save(self):
        with open(TAGS_FILE, "w") as file:
            json.dump(self.tags, file, indent=4, sort_keys=True)

    def remove_keys(self, removed_keys: list[str]):
        if not removed_keys:
            return
        logging.info(f"Removing old entires: {removed_keys}")
        for key in removed_keys:
            self.tags.pop(key)


Hulls = _Hulls()
Tags = _Tags()
