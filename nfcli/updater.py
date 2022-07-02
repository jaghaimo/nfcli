import logging
import os
import shutil
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

URL="https://gitlab.com/nebfltcom/data/-/archive/main/data-main.zip?path=wiki"

def update():
    zip_content = urlopen(URL)
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
