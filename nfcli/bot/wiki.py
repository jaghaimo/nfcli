import logging
from typing import List

from discord import Message, TextChannel
from discord.ext import commands

from nfcli import DISCORD_TOKEN, init_logger
from nfcli.wiki import Wiki

wiki_db = Wiki()
bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
init_logger("bot.wiki.log", logging.INFO)


async def replace_with_previous(channel: TextChannel, link: str, message: str) -> str:
    old_messages: List[Message] = await channel.history(limit=100).flatten()
    for old_message in old_messages:
        if link in old_message.content:
            return f"I have already explained this recently!\n<{old_message.jump_url}>"
    return message


@bot.event
async def on_ready():
    logging.info("Wiki bot initialized")
    for guild in bot.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@bot.command()
async def wiki(ctx: commands.Context, *argv):
    entity = None
    message = (
        "Usage: `!wiki name or part of it`\n"
        "This command is powered by <https://gitlab.com/nebfltcom/data/-/tree/main/wiki>\n"
        "Special thanks to *@Alexbay218#0295*"
    )
    if argv:
        keyword = " ".join(argv)
        entity = wiki_db.get(keyword)
        message = entity.text

    if entity:
        message = await replace_with_previous(ctx.channel, entity.link, message)

    await ctx.reply(message)


def start():
    bot.run(DISCORD_TOKEN)
