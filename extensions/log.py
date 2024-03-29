"""To make text or message logs"""
import os

import hikari as hk
import lightbulb as lb


logger = lb.Plugin("Log Commands", "Keeping a log of data, more to be added later")


@logger.listener(hk.StartingEvent)
async def on_starting(event: hk.StartingEvent) -> None:
    """Event fired on start of bot"""

    logger.bot.d.deleted_hook = await logger.bot.rest.create_webhook(
        channel=1032615074445135903, name="Reze #Deleted-Messages"
    )
    logger.bot.d.updated_hook = await logger.bot.rest.create_webhook(
        channel=1032615074445135903, name="Reze #Edited Messages"
    )


@logger.listener(hk.StoppingEvent)
async def on_stopping(event: hk.StoppingEvent) -> None:
    """Event fired on stopping the bot"""

    await logger.bot.rest.delete_webhook(logger.bot.d.deleted_hook)
    await logger.bot.rest.delete_webhook(logger.bot.d.updated_hook)


@logger.listener(hk.GuildMessageDeleteEvent)
async def delete_log(event: hk.GuildMessageDeleteEvent):
    """Deleted message logger"""
    # limiting it to a particular guild for testing
    if event.guild_id != 997042589117194270:
        return

    print(dir(event))
    old_message = event.old_message
    print(dir(old_message))
    author = old_message.author
    # TO: Fix this shit
    print(old_message.author)
    # if old_message.author.id != '204992650305077248':
    #     return
    # print(author)
    content = old_message.content
    ava = old_message.author.avatar_url
    channel = event.get_channel()
    # await logger.bot.rest.fetch_member(event.guild_id, event.old_message)

    webhook = logger.bot.d.deleted_hook
    await webhook.execute(
        f"Message deleted by {author.mention} in {channel.mention}",
        avatar_url=logger.bot.get_me().avatar_url,
        embed=hk.Embed(description=content, color="92DDEA").set_author(
            name=author.username, icon=ava
        ),
    )


@logger.listener(hk.GuildMessageUpdateEvent)
async def update_log(event: hk.GuildMessageUpdateEvent):
    """Edited message logger"""
    # limiting it to a particular guild for testing
    if event.guild_id != 997042589117194270:
        return

    old_message = event.old_message
    author = old_message.author

    # print(author)
    content = old_message.content
    ava = old_message.author.avatar_url
    channel = event.get_channel()
    # await logger.bot.rest.fetch_member(event.guild_id, event.old_message)

    webhook = logger.bot.d.updated_hook
    await webhook.execute(
        f"Message updated by {author.mention} in {channel.mention}",
        avatar_url=logger.bot.get_me().avatar_url,
        embed=hk.Embed(description=content, color="FEFE95").set_author(
            name=author.username, icon=ava
        ),
    )


@logger.command
@lb.add_checks(lb.owner_only)
@lb.command("logs", "Output the logs as a rar file", pass_options=True, aliases=["log"])
@lb.implements(lb.PrefixCommand)
async def logs_zip(ctx: lb.Context) -> None:
    """Send the log file folder as a .rar file"""

    os.system("rar a logs.rar ./logs")
    await ctx.respond(attachment="logs.rar")
    os.remove("logs.rar")


@logger.command
@lb.add_checks(lb.owner_only)
@lb.command("loglast", "Output the latest log file", pass_options=True, aliases=["ll"])
@lb.implements(lb.PrefixCommand)
async def logs(ctx: lb.Context) -> None:
    """Send the latest log text file"""

    await ctx.respond(attachment="./logs/log.txt")


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(logger)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(logger)
