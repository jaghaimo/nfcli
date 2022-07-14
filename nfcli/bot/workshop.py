import logging

import discord

from nfcli import DISCORD_TOKEN, init_logger
from nfcli.bot import process_workshops

client = discord.Client()
init_logger("bot.workshop.log", logging.DEBUG)


@client.event
async def on_ready():
    logging.info("Workshop bot initialized")
    for guild in client.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    await process_workshops(message),


def start():
    client.run(DISCORD_TOKEN)
