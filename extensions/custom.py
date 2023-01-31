from datetime import datetime
from typing import Optional

import hikari as hk
import lightbulb as lb

from extPlugins.misc import type_of_response 
from extPlugins.misc import injectionRiskError 

import sqlite3

customcmd_plugin = lb.Plugin("Custom Commands")



@customcmd_plugin.command
@lb.command("peakfiction", "Your peak fiction, your goat", aliases=["pf"])
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def peak_fiction(ctx: lb.Context) -> None:
    c = ctx.bot.d.dbcon.cursor()
    query = "SELECT * from userinfo WHERE userid=?"
    args = (ctx.author.id,)
    c.execute(query, args)
    resp = c.fetchone()
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
    # ctx.respond("Enter valid subcommand. Use `-help <command>` to know more")
    pass

@peak_group.child
@lb.option("link", "The link to the series")
@lb.command("add", "Add your favourite if it doesn't exist already", aliases=["a"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def add_subcommand(ctx: lb.Context, link: str) -> None:
    if ";" in link:
        raise injectionRiskError
        return
    botdb = ctx.bot.d.dbcon
    c = botdb.cursor()
    query = "SELECT * from userinfo WHERE userid=?"
    args = (ctx.author.id,)
    c.execute(query, args)
    if c.fetchone():
        await ctx.respond("You already have one, use `-pf` to check it")
        return
    
    query = "INSERT INTO userinfo VALUES (?,?,?)"
    args = (ctx.author.id, ctx.author.username, link)
    c.execute(query, args)
    await ctx.respond(f"Added successfully ✅")
    botdb.commit()

@peak_group.child
@lb.option("link", "The link to the series")
@lb.command("edit", "Change your goat (why?)", aliases=["modify", "e", "u", "update"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def add_subcommand(ctx: lb.Context, link: str) -> None:
    if ";" in link:
        raise injectionRiskError
        return
    botdb = ctx.bot.d.dbcon
    c = botdb.cursor()
    query = "UPDATE userinfo SET favourite=? where userid=?"
    args = (link, ctx.author.id)
    c.execute(query, args)
    await ctx.respond(f"Updated successfully ✅")
    botdb.commit()

@customcmd_plugin.command
@lb.command("command", "Add raw strings for commands", aliases=["cmd"])
@lb.implements(lb.PrefixCommandGroup)
async def cmd_group(ctx: lb.Context) -> None:
    pass

@cmd_group.child
@lb.option("file", "The attachment (if any)", hk.Attachment, required=False)
@lb.option("string", "The string to repeat", str ,required=False)
@lb.option("name", "The name of the command")
@lb.command("add", "Add your favourite if it doesn't exist already", aliases=["a"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def add_subcommand(ctx: lb.Context, name: str, string: str, file: Optional[hk.Attachment]=None) -> None:

    if not string and not file:
        raise lb.NotEnoughArguments
        return

    if ";" in string:
        raise injectionRiskError
        return

    botdb = ctx.bot.d.dbcon
    c = botdb.cursor()
    query = "SELECT * from commands where name=?"
    args = (name,)
    c.execute(query, args)
    if c.fetchone():
        await ctx.respond("Command already exists, try modifying it or using a different name.")
        return


    query = "INSERT INTO commands VALUES (?,?,?)"

    
    args = (name, string, ctx.author.mention)
    c.execute(query, args)
    botdb.commit()
    await ctx.respond(f"Added successfully ✅")
    await ctx.bot.rest.edit_message(ctx.channel_id, ctx.event.message, flags=hk.MessageFlag.SUPPRESS_EMBEDS)

@cmd_group.child
@lb.option("new_string", "The new edited string")
@lb.command("edit", "Edit the string of a custom command", aliases=["e"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def edit_subcommand(ctx: lb.Context, link: str) -> None:
    ...

@cmd_group.child
@lb.option("command", "The command to delete")
@lb.command("delete", "Delete a custom command", aliases=["d"], pass_options=True)
@lb.implements(lb.PrefixSubCommand)
async def delete_subcommand(ctx: lb.Context, link: str) -> None:
    ...

@customcmd_plugin.listener(hk.GuildMessageCreateEvent)
async def custom_commands(event: hk.GuildMessageCreateEvent)-> None:
    if not event.content or not event.content.startswith("-"):
        return

    args = event.content[1:].split()

    
    async with customcmd_plugin.bot.rest.trigger_typing(event.channel_id):
        botdb = customcmd_plugin.bot.d.dbcon
        c = botdb.cursor()

        query = "SELECT name,output FROM commands"
        # args = (link, ctx.author.id)
        c.execute(query)

        commands = c.fetchall()
        
        for item in commands:
            if args[0] == item[0]:
                if type_of_response(item[1]) == 'image':
                    await event.message.respond(hk.Embed().set_image(item[1]))
                else:
                    await event.message.respond(item[1], attachment=item[3] or None)

def load(bot: lb.BotApp) -> None:
    bot.add_plugin(customcmd_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(customcmd_plugin)