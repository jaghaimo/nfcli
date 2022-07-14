import logging
from typing import List

from discord import ApplicationContext, Bot, Message, TextChannel

from nfcli import DISCORD_TOKEN, init_logger
from nfcli.wiki import Wiki

wiki_db = Wiki()
bot = Bot()
init_logger("bot.wiki.log", logging.INFO)


async def replace_with_previous(channel: TextChannel, link: str, message: str) -> str:
    old_messages: List[Message] = await channel.history(limit=100).flatten()
    for old_message in old_messages:
        if old_message.author != bot.user:
            continue
        if link in old_message.content:
            return f"I have already explained this recently!\n<{old_message.jump_url}>"
    return message


@bot.event
async def on_ready():
    logging.info("Wiki bot initialized")
    for guild in bot.guilds:
        logging.info(f"Connected to the guild: {guild.name} (id: {guild.id})")


@bot.command(name="wiki")
async def wiki(ctx: ApplicationContext, *, keywords):
    """Search N:FC wiki data dumps (thanks to @Alexbay218#0295)"""
    entity = wiki_db.get(keywords)
    message = entity.text

    if entity:
        message = await replace_with_previous(ctx.channel, entity.link, message)

    await ctx.respond(message)


def start():
    bot.run(DISCORD_TOKEN)
