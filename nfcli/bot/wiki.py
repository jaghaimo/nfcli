import logging

from discord.ext import commands

from nfcli import DISCORD_TOKEN, init_logger
from nfcli.wiki import Wiki

wiki_db = Wiki()
bot = commands.Bot(command_prefix="!")
init_logger("bot.wiki.log", logging.INFO)


@bot.event
async def on_ready():
    logging.info("Wiki bot initialized")
    for guild in bot.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@bot.command()
async def wiki(ctx, *argv):
    message = (
        "Usage: `!wiki name or part of it`\n"
        "This command is powered by <https://gitlab.com/nebfltcom/data/-/tree/main/wiki>\n"
        "Special thanks to *@Alexbay218#0295*"
    )
    if argv:
        keyword = " ".join(argv)
        entity = wiki_db.get(keyword)
        message = entity.text

    await ctx.reply(message)


def start():
    bot.run(DISCORD_TOKEN)
