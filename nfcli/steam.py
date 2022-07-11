import logging
import os
import subprocess
from glob import glob
from os import path
from posixpath import dirname
from typing import List, Optional, Set
from urllib.parse import parse_qs, urlparse

from steam import webapi

from nfcli import STEAM_API_KEY, STEAM_USERNAME

STEAM_APP_ID = 887570
WORKSHOP_DIR = "~/.steam/steamapps/workshop/content/{}/{}"


def get_local_path(workshop_id: int) -> str:
    return path.expanduser(WORKSHOP_DIR.format(STEAM_APP_ID, workshop_id))


def get_files(directory: str) -> List[str]:
    return glob(path.join(directory, "*.fleet")) + glob(path.join(directory, "*.ship"))


def get_workshop_files(workshop_id: int) -> List[str]:
    """Get cached copy of workshop files, or download on the fly."""
    workshop_path = get_local_path(workshop_id)
    files = get_files(workshop_path)
    if files:
        return files
    download_bulk([workshop_id])
    return get_files(workshop_path)


def download_bulk(workshop_ids: List[int], timeout: Optional[int] = 30):
    steam_cmd = ["steamcmd", "+login", STEAM_USERNAME]
    steam_cmd += ["+workshop_download_item {} {}".format(STEAM_APP_ID, workshop_id) for workshop_id in workshop_ids]
    steam_cmd.append("+quit")
    subprocess.run(steam_cmd, timeout=timeout)


def cache_workshop_files():
    workshop_ids = find_all()
    existing_ids = find_existing()
    missing_ids = workshop_ids.difference(existing_ids)
    if missing_ids:
        download_bulk(missing_ids, 3600)


def find_all() -> Set[int]:
    cursor = "*"
    ids = []
    while cursor:
        params = {
            "appid": STEAM_APP_ID,
            "cursor": cursor,
            "return_tags": True,
            "key": STEAM_API_KEY,
            "numperpage": 100,
            "query_type": 0,
            "search_text": " ",
        }
        results = webapi.get("IPublishedFileService", "QueryFiles", params=params)["response"]
        if "publishedfiledetails" not in results:
            break
        ids += results["publishedfiledetails"]
        cursor = results["next_cursor"]
    total = results["total"]
    logging.info(f"Found {total} workshop files")
    return set(
        [
            int(workshop_id["publishedfileid"])
            for workshop_id in ids
            for tag in workshop_id["tags"]
            if tag["tag"] in ["Fleet", "Ship Template"]
        ]
    )


def find_existing() -> Set[int]:
    local_path = dirname(get_local_path(0))
    return set([int(x) for x in os.listdir(local_path)])


def get_workshop_id(link: str) -> int:
    url = urlparse(link)
    if url.hostname != "steamcommunity.com" or url.path != "/sharedfiles/filedetails/":
        return 0
    params = parse_qs(url.query)
    if "id" not in params:
        return 0
    return int(params["id"][0])
