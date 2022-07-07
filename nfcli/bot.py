import logging
import os
from typing import List

import discord
from dotenv import load_dotenv

from nfcli.parser import parse_any
from nfcli.writer import close_all, delete_all, determine_output_file, get_temp_filename

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
    converted_files: List[discord.File] = []
    tmp_files: List[str] = []
    for file in ship_files + fleet_files:
        logging.info(f"Converting {file}")
        xml_data = await file.read()
        png_file = determine_output_file(file.filename, ".png")
        tmp_file = get_temp_filename(".png")
        entity = parse_any(file.filename, xml_data)
        entity.write(tmp_file)
        converted_files.append(discord.File(open(tmp_file, "rb"), filename=png_file))
        tmp_files.append(tmp_file)

    if converted_files:
        await message.channel.send("", files=converted_files, reference=message)

    close_all(converted_files)
    delete_all(tmp_files)


def start():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    client.run(TOKEN)
