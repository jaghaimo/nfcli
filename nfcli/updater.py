import logging
import os
import shutil
from io import BytesIO
from urllib.request import urlopen, urlretrieve
from zipfile import ZipFile

GITLAB = "https://gitlab.com/"
COMPONENT_DATA = "jaghaimo/nebulousfleetmanager/-/raw/main/nfm/shipcomponentdata.json?inline=false"
SHIP_DATA = "jaghaimo/nebulousfleetmanager/-/raw/main/nfm/shipdata.json?inline=false"
WIKI_DATA = "nebfltcom/data/-/archive/main/data-main.zip?path=wiki"


def update_manager_data():
    logging.debug("Downloading component_data.json")
    urlretrieve(GITLAB + COMPONENT_DATA, "data/component_data.json")
    logging.debug("Downloading ship_data.json")
    urlretrieve(GITLAB + SHIP_DATA, "data/ship_data.json")


def update_wiki_data():
    zip_content = urlopen(GITLAB + WIKI_DATA)
    zipfile = ZipFile(BytesIO(zip_content.read()))
    for member in zipfile.namelist():
        filename = os.path.basename(member)
        if not filename:
            continue
        logging.debug(f"Extracting {filename}")
        source = zipfile.open(member)
        target = open(os.path.join(r"data", filename), "wb")
        with source, target:
            shutil.copyfileobj(source, target)


def update():
    update_manager_data()
    update_wiki_data()
