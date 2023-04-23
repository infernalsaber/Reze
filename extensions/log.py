import hikari as hk
import lightbulb as lb
from hikari import Permissions

from typing import Optional, Union
import isodate
import datetime
import asyncio

logger = lb.Plugin("Log Commands", "Keeping a log of data, more to be added later")


@logger.listener(hk.GuildMessageDeleteEvent)
async def preban(event: hk.GuildMessageDeleteEvent):
    old_message = event.old_message
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



def load(bot: lb.BotApp) -> None:
    bot.add_plugin(logger)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(logger)