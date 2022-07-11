import logging
from asyncio.exceptions import TimeoutError as AsyncioTimeoutError

import discord

from nfcli import DISCORD_TOKEN, init_logger
from nfcli.bot import process_workshops

client = discord.Client()
init_logger("bot.workshop.log", logging.INFO)


@client.event
async def on_ready():
    logging.info("Workshop bot initialized")
    for guild in client.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    try:
        await process_workshops(message),
    except AsyncioTimeoutError:
        await message.channel.send(
            "I'm sorry, but the Steam Workshop integration is currently down.", reference=message
        )


def start():
    client.run(DISCORD_TOKEN)
