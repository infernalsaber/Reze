import os
import asyncio
import dotenv
import datetime
import sqlite3
import logging
import aiohttp

import hikari as hk
import lightbulb as lb
import miru
from lightbulb.ext import tasks

import asyncpraw


dotenv.load_dotenv()


# TODO
# 1. Create a global error handler (shorturl.at/dowBG)✔


# The following snippet is borrowed from:
# https://github.com/Nereg/ARKMonitorBot/blob/1a6cedf34d531bddf0f5b11b3238344192998997/src/main.py#L14


def setup_logging() -> None:
    # get root logger
    root_logger = logging.getLogger("")
    # create a rotating file handler with 1 backup file and 1 megabyte size
    file_handler = logging.handlers.Rotatingfile_handler(
        "./logs/log.txt", "w+", 1_000_000, 1, "UTF-8"
    )
    # create a default console handler
    console_handler = logging.StreamHandler()
    # create a formatting style (modified from hikari)
    formatter = logging.Formatter(
        fmt="%(levelname)-1.1s %(asctime)23.23s %(name)s @ %(lineno)d: %(message)s"
    )
    # add the formatter to both handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # add both handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    # set logging level to info
    root_logger.setLevel(logging.INFO)


bot = lb.BotApp(
    token=os.getenv("BOT_TOKEN"),
    intents=hk.Intents.ALL,
    prefix=["-", "gae", ",,"],
    help_slash_command=True,
    logs="DEBUG",
    owner_ids=[1002964172360929343, 701090852243505212],
)

miru.install(bot)
tasks.load(bot)

bot.load_extensions_from("./extensions/")


@bot.listen()
async def on_starting(event: hk.StartingEvent) -> None:
    bot.d.aio_session = aiohttp.ClientSession()
    bot.d.reddit = asyncpraw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        user_agent="reze",
    )
    bot.d.dbcon = sqlite3.connect("botdb.db")
    bot.d.timeup = datetime.datetime.now().astimezone()
    if not os.path.exists("pictures"):
        os.mkdir("pictures")
        os.mkdir("pictures/visual")
        os.mkdir("videos")
        os.mkdir("logs")
    with open("./logs/log.txt", "w+"):
        pass
    setup_logging()


@bot.listen()
async def on_stopping(event: hk.StoppingEvent) -> None:
    await bot.d.aio_session.close()
    await bot.d.reddit.close()
    bot.d.dbcon.close()


@bot.command
@lb.command("ping", description="The bot's ping")
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def ping(ctx: lb.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")


@bot.listen(lb.CommandErrorEvent)
async def on_error(event: lb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong during invocation of command `{event.context.command.name}`."
        )
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lb.NotOwner):
        await event.context.respond("This command is only usable by bot owner")

    elif isinstance(exception, lb.CommandIsOnCooldown):
        await event.context.respond(
            f"The command is on cooldown, you can use it after {int(exception.retry_after)}s",
            delete_after=int(exception.retry_after),
        )

    elif isinstance(exception, lb.MissingRequiredPermission):
        await event.context.respond(
            "You do not have the necessary permissions to use the command",
            flags=hk.MessageFlag.EPHEMERAL,
        )

    elif isinstance(exception, lb.BotMissingRequiredPermission):
        await event.context.respond("I don't have the permissions to do this 😔")

    elif isinstance(exception, NotImplementedError):
        await event.context.respond(
            "This command has not been implemented or is not open."
        )

    elif isinstance(exception, lb.NotEnoughArguments):
        await event.context.respond(
            f"Missing arguments, use `-help {event.context.command.name}` \
            for the correct invocation"
        )


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        # pass
        import uvloop

        uvloop.install()

    bot.run(
        status=hk.Status.IDLE,
        activity=hk.Activity(name="with your mom's tits", type=hk.ActivityType.PLAYING),
    )
