import logging
import os
from typing import List

import discord
from dotenv import load_dotenv

from nfcli.database import init_database
from nfcli.parser import parse_fleet
from nfcli.writer import (
    close_all,
    delete_all,
    determine_output_file,
    get_temp_filename,
    write_fleet,
)

load_dotenv()
init_database()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()
logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    logging.info("Bot initialized")
    for guild in client.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    fleet_files = [file for file in message.attachments if file.filename.endswith("fleet")]
    converted_files = []  # type: List[discord.File]
    tmp_files = []  # type: List[str]
    for fleet_file in fleet_files:
        logging.info(f"Converting {fleet_file}")
        input = await fleet_file.read()
        fleet = parse_fleet(input)
        png_file = determine_output_file(fleet_file.filename, ".png")
        tmp_file = get_temp_filename(".png")
        write_fleet(fleet, tmp_file)
        converted_files.append(discord.File(open(tmp_file, "rb"), filename=png_file))
        tmp_files.append(tmp_file)

    if converted_files:
        await message.channel.send("", files=converted_files, reference=message)

    close_all(converted_files)
    delete_all(tmp_files)


client.run(TOKEN)
