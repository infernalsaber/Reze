"""Plugin running the background tasks for the bot"""
import os
import glob
import datetime

import asyncio
import isodate

import lightbulb as lb
from lightbulb.ext import tasks


task_plugin = lb.Plugin("Tasks", "Background processes")


@task_plugin.command
@lb.option(
    "task", "The task and the time", str, modifier=lb.OptionModifier.CONSUME_REST
)
@lb.command("remindme", "Set a reminder", pass_options=True, aliases=["remind", "rm"])
@lb.implements(lb.PrefixCommand)
async def remind(ctx: lb.Context, task: str) -> None:
    """Use this command to set a timer after which you would be reminded to do X in your DMs

    Args:
        ctx (lb.Context): Message Context
        task (str): The task to set reminder for
    """

    print(task.split("in"))
    task, time = task.split("in")
    time = time.strip()
    duration = datetime.datetime.now().astimezone() + isodate.parse_duration(
        f"PT{time.upper()}"
    )
    await ctx.respond(
        f"Got it, I'll remind you to {task} in <t:{int(duration.timestamp())}:R>"
    )
    await asyncio.sleep(isodate.parse_duration(f"PT{time.upper()}").total_seconds())
    await ctx.user.send(f"**Reminder to:** {task}")


@tasks.task(d=7)
async def clear_video_files():
    """Clear video files"""
    print("Clearing video Files")
    files = glob.glob("./videos/*")
    for file in files:
        os.remove(file)
    print("Cleared")


@tasks.task(d=14)
async def clear_pic_files():
    """Clear image files"""
    print("Clearing image Files")
    files = glob.glob("./pictures/*")
    for file in files:
        os.remove(file)
    print("Cleared")


@tasks.task(d=30)
async def update_yt_dlp():
    """Update the yt-dlp plugin or it breaks"""
    os.system("yt-dlp -U")
    # Done to prevent the -ytdl and -yts commands from breaking
    print("Updated the package yt-dlp")


@tasks.task(d=30)
async def logs_date():
    """Rotate logger"""
    os.rename("./logs/log.txt", f"./logs/{datetime.date.today()}.txt")


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(task_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(task_plugin)
