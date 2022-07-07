import asyncio
import logging
import os
import re
from typing import List, TextIO
from urllib.parse import parse_qs, urlparse

import discord

from nfcli import DISCORD_TOKEN, load_path
from nfcli.parser import parse_any, parse_mods
from nfcli.printer import FleetPrinter
from nfcli.steam import download_workshop
from nfcli.writer import delete_temporary, determine_output_png, get_temp_filename

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
        process_files(message),
        process_workshops(message),
    )


async def process_file(message: discord.Message, xml_data: str, filename: str):
    logging.info(f"Converting {filename}")
    png_file = determine_output_png(filename)
    tmp_file = get_temp_filename(".png")
    entity = parse_any(filename, xml_data)
    entity.write(tmp_file)
    converted_file = discord.File(open(tmp_file, "rb"), filename=png_file)
    mod_deps = parse_mods(xml_data)
    mods = FleetPrinter.get_mods(mod_deps, "<", ">")
    await message.channel.send(f"Hull types: {entity.hulls}{mods}", files=[converted_file], reference=message)
    cleanup(converted_file, tmp_file)


async def process_files(message: discord.Message):
    ship_files = [file for file in message.attachments if file.filename.endswith("ship")]
    fleet_files = [file for file in message.attachments if file.filename.endswith("fleet")]
    for file in ship_files + fleet_files:
        xml_data = await file.read()
        await process_file(message, xml_data, file.filename)


async def process_workshops(message: discord.Message):
    link_regex = re.compile("((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", re.DOTALL)
    links = re.findall(link_regex, message.content)
    for link_data in links:
        url = urlparse(link_data[0])
        if url.hostname != "steamcommunity.com" or url.path != "/sharedfiles/filedetails/":
            continue

        params = parse_qs(url.query)
        if "id" not in params:
            continue

        input_file = download_workshop(params["id"])[0]
        xml_data = load_path(input_file)
        await process_file(message, xml_data, input_file)
        delete_temporary(input_file)


def cleanup(open_file: List[TextIO], filename: str):
    open_file.close()
    os.unlink(filename)


def start():
    client.run(DISCORD_TOKEN)
