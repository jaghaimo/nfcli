import json
import logging
from glob import glob
from typing import Dict, Optional


class Database:
    def __init__(self) -> None:
        self.hulls = {}
        self.tags = self._load_json("data/tags.json")
        self._load_hulls("data/hulls.json")

    def _load_hulls(self, path: str) -> Dict:
        hull_files = self._load_json(path)
        for file, namespace in hull_files.items():
            hull = self._load_json(file)
            key = hull["key"]
            self.hulls[f"{namespace}/{key}"] = hull

    def _load_json(self, path: str) -> Dict:
        try:
            f = open(path, "r")
        except EnvironmentError:
            return {}
        else:
            return json.load(f)

    def get_component_tag(self, socket: str) -> Optional[str]:
        if socket in self.tags:
            return self.tags.get(socket)
        return None

    def get_hull_data(self, hull: str) -> Dict:
        if hull in self.hulls:
            return self.hulls.get(hull)
        return {}


db = Database()
