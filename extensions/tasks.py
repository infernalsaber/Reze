import datetime
# from typing import Optional
import asyncio
import isodate
import os
import glob

import hikari as hk
import lightbulb as lb
from lightbulb.ext import tasks
# from extPlugins.misc import get_top_colour

task_plugin = lb.Plugin("Tasks", "Background processes")

"""
#TODO

"""

@task_plugin.command
@lb.option(
    "task", "The task and the time", str, modifier=lb.OptionModifier.CONSUME_REST
)
@lb.command("remindme", "Set a reminder", pass_options=True, aliases=["remind", "rm"])
@lb.implements(lb.PrefixCommand)
async def reminder(ctx: lb.Context, task: str) -> None:
    """Use this command to set a timer after which you would be reminded to do X in your DMs

    Args:
        ctx (lb.Context): Message Context
        task (str): The task to set reminder for
    """
    print(task.split("in"))
    task, time = task.split("in")
    time = time.strip()
    duration = datetime.datetime.now().astimezone() + isodate.parse_duration(f"PT{time.upper()}")
    await ctx.respond(f"Got it, I'll remind you to {task} in <t:{int(duration.timestamp())}:R>")
    await asyncio.sleep(isodate.parse_duration(f"PT{time.upper()}").total_seconds())
    await ctx.user.send(f"**Reminder to:** {task}")

@tasks.task(d=7)
async def clear_media_files():
    print("Clearing Media Files")
    files = glob.glob("./videos/*")
    for f in files:
        os.remove(f)
    print("Cleared")

@tasks.task(d=14)
async def clear_media_files():
    print("Clearing Media Files")
    files = glob.glob("./pictures/*")
    for f in files:
        os.remove(f)
    print("Cleared")

def load(bot: lb.BotApp) -> None:
    bot.add_plugin(task_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(task_plugin)