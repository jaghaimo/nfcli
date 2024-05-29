import logging
import os
import subprocess
from distutils.dir_util import remove_tree
from glob import glob
from os import path
from posixpath import dirname
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from steam import webapi

from nfcli import init_logger

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USERNAME = os.getenv("STEAM_USERNAME")
STEAM_APP_ID = 887570
WORKSHOP_DIR = "~/Steam/steamapps/workshop/content/{}/{}"


def get_player_count() -> int:
    params = {"appid": STEAM_APP_ID}
    query = webapi.get("ISteamUserStats", "GetNumberOfCurrentPlayers", params=params)
    if query is None:
        return -1
    results = query.get("response")
    if results is None:
        return -1
    return results.get("player_count", -1)


def get_local_path(workshop_id: int) -> str:
    return path.expanduser(WORKSHOP_DIR.format(STEAM_APP_ID, workshop_id))


def get_files(directory: str) -> list[str]:
    return glob(path.join(directory, "*.fleet")) + glob(path.join(directory, "*.ship"))


def get_workshop_files(workshop_id: int, throw_if_not_found: bool | None = False) -> list[str]:
    """Get cached copy of workshop files, or download on the fly."""
    workshop_path = get_local_path(workshop_id)
    files = get_files(workshop_path)
    if files:
        return files
    workshop_ids = find_all()
    if workshop_id not in workshop_ids:
        return []
    if throw_if_not_found:
        raise RuntimeError(f"I'm sorry, but the workshop item {workshop_id} has not yet been cached.")
    logging.info(f"Downloading workshop item {workshop_id}.")
    download_bulk({workshop_id})
    return get_files(workshop_path)


def download_bulk(workshop_ids: set[int], timeout: int = 30):
    steam_cmd = ["steamcmd", "+login", STEAM_USERNAME]
    steam_cmd += [f"+workshop_download_item {STEAM_APP_ID} {workshop_id}" for workshop_id in workshop_ids]
    steam_cmd.append("+quit")
    subprocess.run(steam_cmd, timeout=timeout)


def cache_workshop_files():
    init_logger(None, logging.INFO)
    workshop_items = find_all()
    invalidate_cache(workshop_items)
    workshop_ids = set(workshop_items.keys())
    existing_ids = find_existing()
    missing_ids = workshop_ids.difference(existing_ids)
    if missing_ids:
        logging.info(f"Downloading missing {len(missing_ids)} workshop files...")
        download_bulk(missing_ids, 3600)


def invalidate_cache(workshop_items: dict[int, dict]) -> None:
    for workshop_id, workshop_item in workshop_items.items():
        workshop_path = get_local_path(workshop_id)
        if not os.path.exists(workshop_path):
            continue
        mtime = os.path.getmtime(workshop_path)
        if mtime < workshop_item["time_updated"]:
            logging.info(f"Invalidating workshop item {workshop_id}.")
            remove_tree(workshop_path)


def is_valid(tags: list[dict]) -> bool:
    return any(tag["tag"].lower() in ["fleet", "ship template"] for tag in tags)


def find_all() -> dict[int, dict]:
    cursor = "*"
    total = 0
    all_items = {}
    while cursor:
        params = {
            "appid": STEAM_APP_ID,
            "cursor": cursor,
            "return_tags": True,
            "key": STEAM_API_KEY,
            "numperpage": 100,
            "query_type": 21,
        }
        query = webapi.get("IPublishedFileService", "QueryFiles", params=params)
        if query is None:
            break
        results = query.get("response")
        if results is None or "publishedfiledetails" not in results:
            break
        cursor = results["next_cursor"]
        items = results["publishedfiledetails"]
        total = results["total"]
        add_items(all_items, items)
    valid = len(all_items)
    logging.info(f"Found {total} workshop files with {valid} being valid...")
    return all_items


def add_items(all_items: dict[int, dict], items: list[dict]) -> None:
    valid_items = [item for item in items if "tags" in item and is_valid(item["tags"])]
    for valid_item in valid_items:
        item_id = int(valid_item["publishedfileid"])
        all_items[item_id] = valid_item


def find_existing() -> set[int]:
    local_path = dirname(get_local_path(0))
    if not os.path.exists(local_path):
        return set()
    return {int(x) for x in os.listdir(local_path)}


def get_workshop_id(link: str) -> int:
    url = urlparse(link)
    if url.hostname != "steamcommunity.com" or url.path != "/sharedfiles/filedetails/":
        return 0
    params = parse_qs(url.query)
    if "id" not in params:
        return 0
    return int(params["id"][0])
