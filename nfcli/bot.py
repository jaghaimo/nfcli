import asyncio
import logging
import os
import re
import tempfile
from posixpath import basename
from typing import List

import discord
from discord import File, Message
from discord.ext import tasks
from dotenv import load_dotenv
from genericpath import exists

from nfcli import determine_output_png, init_logger, load_path
from nfcli.models import Lobbies
from nfcli.parsers import parse_any, parse_mods
from nfcli.printers import Printer
from nfcli.sqlite import create_connection, fetch_lobby_data, insert_lobby_data, insert_usage_data
from nfcli.steam import get_player_count, get_workshop_files, get_workshop_id
from nfcli.wiki import Wiki

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNELS = [int(discord_channel) for discord_channel in os.getenv("DISCORD_CHANNELS").split(",")]

wiki_db = Wiki()
connection = create_connection()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)
init_logger("bot.log", logging.INFO)


def get_temp_filename(ext: str) -> str:
    return tempfile.mktemp() + ext


def is_supported(filename: str) -> bool:
    extensions = ["fleet", "missile", "ship"]
    return any([filename.endswith(extension) for extension in extensions])


async def process_file(message: Message, xml_data: str, filename: str, with_fleet_file: bool):
    """Process one file content."""
    async with message.channel.typing():
        logging.info(f"Converting file {filename}")
        png_file = determine_output_png(filename)
        tmp_file = get_temp_filename(".png")
        entity = parse_any(filename, xml_data)
        entity.write(tmp_file)
        all_files = []
        if exists(tmp_file):
            converted_file = File(open(tmp_file, "rb"), filename=png_file)
            all_files.append(converted_file)
        if with_fleet_file:
            all_files.append(File(open(filename, "rb"), filename=basename(filename)))
        mod_deps = parse_mods(xml_data)
        mods = Printer.get_mods(mod_deps, "<", ">")
        await message.reply(f"{entity.text}{mods}", files=all_files)
        converted_file.close()
        os.unlink(tmp_file)


async def process_uploads(message: Message):
    """Process uploaded files."""
    files = [file for file in message.attachments if is_supported(file.filename)]
    if files:
        insert_usage_data(connection, message.guild.id, message.author.id, files)
    for file in files:
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
        await message.reply(exception)


async def process_old_wiki(message: Message):
    """Adds a friendly reminded to use slash command instead."""
    is_wiki = message.content[1:5].lower() == "wiki"
    if is_wiki:
        reply = await message.reply(
            "Hey dummy, stop spamming the channel and use `/wiki` command instead!\n"
            "In case you missed the tutorial: type `/wiki`, press enter, type keywords, press enter again.\n"
            "This message will self destruct in few seconds. I hope yours too!"
        )
        await asyncio.sleep(9)
        await reply.delete()


async def process_workshops(message: Message):
    """Extract and process workshop links."""
    link_regex = re.compile(r"https?:\/\/steamcommunity\.com\/sharedfiles\/filedetails\S+id=\d+")
    links = re.findall(link_regex, message.content)
    workshop_ids = set()
    for link_data in links:
        workshop_ids.add(get_workshop_id(link_data))

    for workshop_id in workshop_ids:
        await process_workshop(message, workshop_id)


def process_lobby_data(message: Message):
    """Extract and process lobby data from subscribed channel."""
    logging.debug("Checking incoming message")
    Lobbies._parse_data(message.content)
    logging.debug("Adding new lobby data")
    insert_lobby_data(connection, message.author.name, message.content)


async def replace_with_previous(channel: discord.TextChannel, link: str, message: str) -> str:
    old_messages: List[discord.Message] = await channel.history(limit=100).flatten()
    for old_message in old_messages:
        if old_message.author != bot.user:
            continue
        if link in old_message.content:
            return f"I have already explained this recently!\n<{old_message.jump_url}>"
    return message


@bot.event
async def on_ready():
    logging.info("Discord bot initialized")
    for guild in bot.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")
    status_changer.start()


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.channel.id in DISCORD_CHANNELS and message.author.bot:
        process_lobby_data(message)
    else:
        await process_old_wiki(message)
        await process_workshops(message)
        await process_uploads(message)


@bot.slash_command(name="wiki")
async def wiki_slash(ctx: discord.ApplicationContext, *, keywords: str):
    """Search N:FC wiki data dumps provided by @Alexbay218#0295"""
    entity = wiki_db.get(keywords)
    message = entity.text
    if entity:
        message = await replace_with_previous(ctx.channel, entity.link, message)
    await ctx.respond(message)


@bot.slash_command(name="lobbies")
async def lobbies_slash(ctx: discord.ApplicationContext):
    """Report number of lobbies in the game (semi-live data provided by volunteers)."""
    lobby = fetch_lobby_data(connection)
    await ctx.respond(lobby)


@tasks.loop(seconds=60.0)
async def status_changer():
    player_count = get_player_count()
    name = f"{str(player_count)} fleets"
    if player_count == -1:
        name = "undisclosed number of fleets"
    elif player_count == 0:
        name = "empty shipyard"
    elif player_count == 1:
        name = "just one fleet"
    activity = discord.Activity(type=discord.ActivityType.watching, name=name)
    await bot.change_presence(activity=activity)


def start():
    bot.run(DISCORD_TOKEN)
