import asyncio
import functools
import logging
import time
from distutils.dir_util import copy_tree
from glob import glob
from os import mkdir, path
from tempfile import mkdtemp
from typing import Callable, Coroutine, List, Optional
from urllib.parse import parse_qs, urlparse

from steam import webapi
from steamctl.commands.workshop.gcmds import cmd_workshop_download
from tqdm import tqdm

from nfcli import STEAM_API_KEY, STEAM_USERNAME
from nfcli.writer import delete_temporary

NFC_STEAM_APP_ID = 887570
WORKSHOP_DIR = "workshop"
WORKSHOP_TIMEOUT = 60


def thread_with_timeout(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        future = loop.run_in_executor(None, wrapped)
        return await asyncio.wait_for(future, WORKSHOP_TIMEOUT)

    return wrapper


def get_path(workshop_id: int) -> str:
    return path.join(WORKSHOP_DIR, str(workshop_id))


def get_workshop_files(workshop_id: int, sleep: Optional[int] = 0) -> List[str]:
    """Get cached copy of workshop files, or download on the fly."""
    path = get_path(workshop_id)
    files = get_files(path)
    if files:
        return files
    time.sleep(sleep)
    return asyncio.run(download_from_workshop(workshop_id))


@thread_with_timeout
def download_from_workshop(workshop_id: int) -> List[str]:
    args = get_args(workshop_id)
    cmd_workshop_download(args)
    path = get_path(workshop_id)
    copy_tree(args.output, path)
    delete_temporary(args.output)
    return get_files(path)

def download_all():
    workshop_ids = find_all()
    for _, workshop_id in enumerate(tqdm(workshop_ids)):
        get_workshop_files(workshop_id, 1)

def find_all() -> List[int]:
    cursor = "*"
    ids = []
    while cursor:
        params = {
            "appid": NFC_STEAM_APP_ID,
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
    return [workshop_id["publishedfileid"] for workshop_id in ids for tag in workshop_id["tags"] if tag["tag"] in ["Fleet", "Ship Template"]]


def get_args(workshop_id: int) -> object:
    args = type("", (), {})()
    args.anonymous = False
    args.apikey = STEAM_API_KEY
    args.appid = NFC_STEAM_APP_ID
    args.cell_id = None
    args.id = workshop_id
    args.output = mkdtemp()
    args.user = STEAM_USERNAME
    args.no_progress = True
    args.no_directories = False
    return args


def get_files(directory: str) -> List[str]:
    return glob(path.join(directory, "*.fleet")) + glob(path.join(directory, "*.ship"))


def get_workshop_id(link: str) -> int:
    url = urlparse(link)
    if url.hostname != "steamcommunity.com" or url.path != "/sharedfiles/filedetails/":
        return 0
    params = parse_qs(url.query)
    if "id" not in params:
        return 0
    return int(params["id"][0])
