import logging
import os

import discord
from dotenv import load_dotenv

from nfcli.database import init_database
from nfcli.parser import parse_fleet
from nfcli.writer import write_fleet

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

    fleet_files = [
        file for file in message.attachments if file.filename.endswith("fleet")
    ]
    converted_files = []
    for fleet_file in fleet_files:
        logging.info(f"Converting {fleet_file}")
        input = await fleet_file.read()
        fleet = parse_fleet(input)
        png_file = write_fleet(fleet, fleet_file.filename)
        converted_files += [
            discord.File(open(png_file, "rb"), filename=png_file, spoiler=True)
        ]

    if converted_files:
        await message.channel.send("", files=converted_files, reference=message)


client.run(TOKEN)
