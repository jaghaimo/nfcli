import logging
import os
from typing import List, TextIO

import discord
from dotenv import load_dotenv

from nfcli.parser import parse_any, parse_mods
from nfcli.printer import FleetPrinter
from nfcli.writer import determine_output_file, get_temp_filename

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

    ship_files = [file for file in message.attachments if file.filename.endswith("ship")]
    fleet_files = [file for file in message.attachments if file.filename.endswith("fleet")]
    for file in ship_files + fleet_files:
        logging.info(f"Converting {file}")
        xml_data = await file.read()
        png_file = determine_output_file(file.filename, ".png")
        tmp_file = get_temp_filename(".png")
        entity = parse_any(file.filename, xml_data)
        entity.write(tmp_file)
        converted_file = discord.File(open(tmp_file, "rb"), filename=png_file)
        mod_deps = parse_mods(xml_data)
        mods = FleetPrinter.get_mods(mod_deps, "<", ">")
        await message.channel.send(f"Hull types: {entity.hulls}{mods}", files=[converted_file], reference=message)
        cleanup(converted_file, tmp_file)


def cleanup(open_file: List[TextIO], filename: str):
    open_file.close()
    os.unlink(filename)


def start():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    client.run(TOKEN)
