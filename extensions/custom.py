"""A module where you make custom commands, or define your parent shill"""
from typing import Optional

import hikari as hk
import lightbulb as lb

from extPlugins.misc import type_of_response
from extPlugins.misc import InjectionRiskError


customcmd_plugin = lb.Plugin("Custom Commands")


@customcmd_plugin.command
@lb.command("peakfiction", "Your peak fiction, your goat", aliases=["pf", "goat"])
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def peak_fiction(ctx: lb.Context) -> None:
    """Echo your favourite series' link

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
    """

    cur = ctx.bot.d.dbcon.cursor()
    query = "SELECT * from userinfo WHERE userid=?"
    args = (ctx.author.id,)
    cur.execute(query, args)
    resp = cur.fetchone()
    if not resp or len(resp) == 0:
        await ctx.respond(
            "Nothing found, add your goat using `-peakfiction add` or `-pf a` for short."
        )
        return
    await ctx.respond(resp[2])


@customcmd_plugin.command
@lb.command("peakfictionmodify", "Modify, add or delete your goat", aliases=["pfm"])
@lb.implements(lb.PrefixCommandGroup)
async def peak_group(ctx: lb.Context) -> None:
    """Do modifications to your favourite series

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
    """
    # ctx.respond("Enter valid subcommand. Use `-help <command>` to know more")


@peak_group.child
@lb.option("link", "The link to the series")
@lb.command(
    "add",
    "Add your favourite if it doesn't exist already",
    aliases=["a"],
    pass_options=True,
)
@lb.implements(lb.PrefixSubCommand)
async def add_pf(ctx: lb.Context, link: str) -> None:
    """Add your favourite series if not already there

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        link (str): Link of ther series

    Raises:
        InjectionRiskError: In case a statement seems it might inject SQL Code
    """

    if ";" in link:
        raise InjectionRiskError

    botdb = ctx.bot.d.dbcon
    cur = botdb.cursor()
    query = "SELECT * from userinfo WHERE userid=?"
    args = (ctx.author.id,)
    cur.execute(query, args)
    if cur.fetchone():
        await ctx.respond("You already have one, use `-pf` to check it")
        return

    query = "INSERT INTO userinfo VALUES (?,?,?)"
    args = (ctx.author.id, ctx.author.username, link)
    cur.execute(query, args)
    await ctx.respond("Added successfully ✅")
    botdb.commit()


@peak_group.child
@lb.option("link", "The link to the series")
@lb.command(
    "edit",
    "Change your goat (why?)",
    aliases=["modify", "e", "u", "update"],
    pass_options=True,
)
@lb.implements(lb.PrefixSubCommand)
async def edit_pf(ctx: lb.Context, link: str) -> None:
    """Edit your favourite series if you have a new one now

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        link (str): New link

    Raises:
        InjectionRiskError: In case a statement seems it might inject SQL Code
    """

    if ";" in link:
        raise InjectionRiskError

    botdb = ctx.bot.d.dbcon
    cur = botdb.cursor()
    query = "UPDATE userinfo SET favourite=? where userid=?"
    args = (link, ctx.author.id)
    cur.execute(query, args)
    await ctx.respond("Updated successfully ✅")
    botdb.commit()


@customcmd_plugin.command
@lb.command("command", "Add raw strings for commands", aliases=["cmd"])
@lb.implements(lb.PrefixCommandGroup)
async def cmd_group(ctx: lb.Context) -> None:
    """Add custom text/img commands

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
    """


@cmd_group.child
@lb.option("file", "The attachment (if any)", hk.Attachment, required=False)
@lb.option(
    "string",
    "The string to repeat",
    str,
    modifier=lb.OptionModifier.CONSUME_REST,
    required=False,
)
@lb.option("name", "The name of the command")
@lb.command(
    "add",
    "Add your favourite if it doesn't exist already",
    aliases=["a"],
    pass_options=True,
)
@lb.implements(lb.PrefixSubCommand)
async def add_subcommand(
    ctx: lb.Context, name: str, string: str, file: Optional[hk.Attachment] = None
) -> None:
    """Add a new command

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        name (str): Name to trigger the command
        string (str): The string to repeat
        file (Optional[hk.Attachment], optional): The attachemnt to send, if any (Not implemented)

    Raises:
        lb.NotEnoughArguments: Insufficient argument ie. no text
        InjectionRiskError: In case a statement seems it might inject SQL Code
    """

    if not string and not file:
        raise lb.NotEnoughArguments

    if ";" in string:
        raise InjectionRiskError

    botdb = ctx.bot.d.dbcon
    cur = botdb.cursor()
    query = "SELECT * from commands where name=?"
    args = (name,)
    cur.execute(query, args)
    if cur.fetchone():
        await ctx.respond(
            "Command already exists, try modifying it or using a different name."
        )
        return

    query = "INSERT INTO commands VALUES (?,?,?, ?)"

    args = (name, string, ctx.author.mention, None)
    cur.execute(query, args)
    botdb.commit()
    await ctx.event.message.add_reaction("✅")
    # await ctx.respond(f"Added successfully ✅")
    await ctx.bot.rest.edit_message(
        ctx.channel_id, ctx.event.message, flags=hk.MessageFlag.SUPPRESS_EMBEDS
    )


# @cmd_group.child
# @lb.option("new_string", "The new edited string")
# @lb.command(
#     "edit", "Edit the string of a custom command", aliases=["e"], pass_options=True
# )
# @lb.implements(lb.PrefixSubCommand)
# async def edit_subcommand(ctx: lb.Context, link: str) -> None:
#     ...


@cmd_group.child
@lb.option("command", "The command to delete")
@lb.command("delete", "Delete a custom command", aliases=["d"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def delete_subcommand(ctx: lb.Context, command: str) -> None:
    """_summary_

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        command (str): The command to delete

    Raises:
        InjectionRiskError: In case a statement seems it might inject SQL Code
    """

    if ";" in command:
        raise InjectionRiskError

    botdb = ctx.bot.d.dbcon
    cur = botdb.cursor()
    query = "DELETE FROM commands WHERE name=?"
    args = (command,)
    cur.execute(query, args)
    await ctx.respond(f"Deleted command: `{command}`")


@customcmd_plugin.listener(hk.GuildMessageCreateEvent)
async def custom_commands(event: hk.GuildMessageCreateEvent) -> None:
    """Listener to listen for and execute custom commmands

    Args:
        event (hk.GuildMessageCreateEvent): The event to listen for
    """

    if not event.content or not event.content.startswith("-"):
        return

    args = event.content[1:].split()

    async with customcmd_plugin.bot.rest.trigger_typing(event.channel_id):
        botdb = customcmd_plugin.bot.d.dbcon
        cur = botdb.cursor()

        query = "SELECT name,output FROM commands"
        cur.execute(query)
        commands = cur.fetchall()

        for item in commands:
            if args[0] == item[0]:
                if type_of_response(item[1]) == "image":
                    await event.message.respond(hk.Embed().set_image(item[1]))
                else:
                    await event.message.respond(item[1])


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(customcmd_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(customcmd_plugin)
