import asyncio
import logging
import re
from posixpath import basename

import discord

from nfcli import DISCORD_TOKEN, load_path
from nfcli.parser import parse_any, parse_mods
from nfcli.printer import FleetPrinter
from nfcli.steam import download_workshop, get_workshop_id
from nfcli.writer import close_and_delete, delete_temporary, determine_output_png, get_temp_filename

client = discord.Client()
logging.basicConfig(level=logging.INFO, force=True)


@client.event
async def on_ready():
    logging.info("Bot initialized")
    for guild in client.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    await asyncio.gather(
        process_uploads(message),
        process_workshops(message),
    )


async def process_file(message: discord.Message, xml_data: str, filename: str, with_fleet_file: bool):
    """Process one file content."""
    logging.info(f"Converting {filename}")
    png_file = determine_output_png(filename)
    tmp_file = get_temp_filename(".png")
    entity = parse_any(filename, xml_data)
    entity.write(tmp_file)
    converted_file = discord.File(open(tmp_file, "rb"), filename=png_file)
    all_files = [converted_file]
    if with_fleet_file:
        all_files.append(discord.File(open(filename, "rb"), filename=basename(filename)))
    mod_deps = parse_mods(xml_data)
    mods = FleetPrinter.get_mods(mod_deps, "<", ">")
    await message.channel.send(f"Hull types: {entity.hulls}{mods}", files=all_files, reference=message)
    close_and_delete(converted_file, tmp_file)


async def process_uploads(message: discord.Message):
    """Process uploaded files."""
    ship_files = [file for file in message.attachments if file.filename.endswith("ship")]
    fleet_files = [file for file in message.attachments if file.filename.endswith("fleet")]
    for file in ship_files + fleet_files:
        xml_data = await file.read()
        await process_file(message, xml_data, file.filename, with_fleet_file=False)


async def process_workshop(message: discord.Message, workshop_id: int):
    """Process one workshop id."""
    input_files = download_workshop(workshop_id)
    for input_file in input_files:
        xml_data = load_path(input_file)
        await process_file(message, xml_data, input_file, with_fleet_file=True)
        delete_temporary(input_file)


async def process_workshops(message: discord.Message):
    """Extract and process workshop links."""
    link_regex = re.compile(r"https?:\/\/steamcommunity\.com\/sharedfiles\/filedetails\S+")
    links = re.findall(link_regex, message.content)
    workshop_ids = set()
    for link_data in links:
        workshop_ids.add(get_workshop_id(link_data))

    for workshop_id in workshop_ids:
        await process_workshop(message, workshop_id)


def start():
    client.run(DISCORD_TOKEN)
