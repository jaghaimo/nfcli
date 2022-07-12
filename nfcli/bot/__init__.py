import logging
import re
from posixpath import basename

from discord import File, Message

from nfcli import load_path
from nfcli.parser import parse_any, parse_mods
from nfcli.printer import FleetPrinter
from nfcli.steam import get_workshop_files, get_workshop_id
from nfcli.writer import close_and_delete, determine_output_png, get_temp_filename


async def process_file(message: Message, xml_data: str, filename: str, with_fleet_file: bool):
    """Process one file content."""
    logging.info(f"Converting {filename}")
    png_file = determine_output_png(filename)
    tmp_file = get_temp_filename(".png")
    entity = parse_any(filename, xml_data)
    entity.write(tmp_file)
    converted_file = File(open(tmp_file, "rb"), filename=png_file)
    all_files = [converted_file]
    if with_fleet_file:
        all_files.append(File(open(filename, "rb"), filename=basename(filename)))
    mod_deps = parse_mods(xml_data)
    mods = FleetPrinter.get_mods(mod_deps, "<", ">")
    await message.channel.send(f"{entity.text}{mods}", files=all_files, reference=message)
    close_and_delete(converted_file, tmp_file)


async def process_uploads(message: Message):
    """Process uploaded files."""
    ship_files = [file for file in message.attachments if file.filename.endswith("ship")]
    fleet_files = [file for file in message.attachments if file.filename.endswith("fleet")]
    for file in ship_files + fleet_files:
        xml_data = await file.read()
        await process_file(message, xml_data, file.filename, with_fleet_file=False)


async def process_workshop(message: Message, workshop_id: int):
    """Process one workshop id."""
    logging.info(f"Processing workshop item {workshop_id}")
    try:
        input_files = get_workshop_files(workshop_id, throw_if_not_found=True)
        for input_file in input_files:
            xml_data = load_path(input_file)
            await process_file(message, xml_data, input_file, with_fleet_file=True)
    except RuntimeError as exception:
        logging.error(exception)
        await message.channel.send(exception, reference=message)


async def process_workshops(message: Message):
    """Extract and process workshop links."""
    link_regex = re.compile(r"https?:\/\/steamcommunity\.com\/sharedfiles\/filedetails\S+id=\d+")
    links = re.findall(link_regex, message.content)
    workshop_ids = set()
    for link_data in links:
        workshop_ids.add(get_workshop_id(link_data))

    for workshop_id in workshop_ids:
        await process_workshop(message, workshop_id)
