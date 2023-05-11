import hikari as hk
import lightbulb as lb
from hikari import Permissions

from typing import Optional, Union
import isodate
import datetime
import asyncio

import os

logger = lb.Plugin("Log Commands", "Keeping a log of data, more to be added later")


@logger.listener(hk.GuildMessageDeleteEvent)
async def log(event: hk.GuildMessageDeleteEvent):
    print(dir(event))
    old_message = event.old_message
    print(dir(old_message))
    author = old_message.author
    # old_message.author.is_bot
    if old_message.author.id != '204992650305077248':
        return
    # print(author)
    content = old_message.content
    ava = old_message.author.avatar_url
    channel = event.get_channel()
    # await logger.bot.rest.fetch_member(event.guild_id, event.old_message)

    await logger.bot.rest.create_message(
        channel,
        f"Message deleted by {author.mention} in {channel.mention}",
        embed=hk.Embed(
            description=content,
            color=old_message.author.accent_color
        )
        .set_author(
            name= author.username,
            icon=ava
        ),
        
        # content=    
    )

@logger.command
@lb.add_checks(
    lb.owner_only
)
@lb.command("logs", "Output the logs as a rar file", pass_options=True, aliases=["log"])
@lb.implements(lb.PrefixCommand)
async def logs(ctx: lb.Context) -> None:
    os.system('rar a logs.rar ./logs')
    await ctx.respond(attachment="logs.rar")
    os.remove("logs.rar")

@logger.command
@lb.add_checks(
    lb.owner_only
)
@lb.command("loglast", "Output the latest log file", pass_options=True, aliases=["ll"])
@lb.implements(lb.PrefixCommand)
async def logs(ctx: lb.Context) -> None:
    await ctx.respond(attachment="./logs/log.txt")

def load(bot: lb.BotApp) -> None:
    bot.add_plugin(logger)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(logger)