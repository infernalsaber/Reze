from datetime import datetime
from typing import Optional

import hikari as hk
import lightbulb as lb
import miru
from miru.ext import nav

from extPlugins.misc import CustomPrevButton, CustomNextButton

walkthrough = lb.Plugin("Walkthrough", "Get to know all the cool commands")


# import time


@walkthrough.command
@lb.command(
    "walkthrough",
    "Get a walktrhough using the bot",
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def walkthrough_cmd(ctx: lb.Context) -> None:
    # Lookup
    pages = []
    pages.append(
        hk.Embed(
            title="Lookup", description="Lookup anime, manga or characters"
        ).set_image("https://files.catbox.moe/72cpf3.gif")
    )
    # Youtubesearch
    pages.append(
        hk.Embed(
            title="Search YouTube",
            description="Get your music off YT. \n**NOTE:** If you have the link, consider using the -ytdl command",
        ).set_image("https://files.catbox.moe/6iltvy.gif")
    )
    # DB
    pages.append(
        hk.Embed(
            title="Danbooru",
            description="Find fanart on danbooru (eg. -db tag1+tag2) \nCurrently in review",
        ).set_image("https://i.imgur.com/c9h6Y79.png")
    )
    # Subreddit
    pages.append(
        hk.Embed(
            title="Subreddit", description="Get hot posts from a sr, or multiple"
        ).set_image("https://i.imgur.com/VQjOvtI.png")
    )
    # Search
    pages.append(
        hk.Embed(
            title="Google images",
            description="Find the google image results for a query",
        ).set_image("https://i.imgur.com/R3g1uW9.png")
    )
    # Search
    pages.append(
        hk.Embed(title="3x3", description="Fast af 3x3 maker").set_image(
            "https://i.imgur.com/81SCLlr.png"
        )
    )
    # Reminders
    pages.append(
        hk.Embed(
            title="Reminder", description="Set a reminder. Eg. -rm sleep in 1h4m"
        ).set_image("https://i.imgur.com/EhllQif.png")
    )
    # ImageTools
    pages.append(
        hk.Embed(
            title="Image Tools", description="Fun/useful image modifications"
        ).set_image("https://files.catbox.moe/552pkx.gif")
    )
    # Color info
    pages.append(
        hk.Embed(title="Color", description="Get a color and its info").set_image(
            "https://i.imgur.com/ymqZyvy.png"
        )
    )
    # Plot
    pages.append(
        hk.Embed(
            title="Plot graphs", description="Make cool comparision graphs"
        ).set_image("https://i.imgur.com/CwYQXi5.png")
    )
    pages.append(
        hk.Embed(
            title="Plot graphs", description="Make cool comparision graphs"
        ).set_image("https://i.imgur.com/lV1S9OC.png")
    )

    buttons = [CustomPrevButton(), nav.IndicatorButton(), CustomNextButton()]

    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    # print("Time is ", time.time()-timeInit)
    await navigator.send(ctx.channel_id)


@walkthrough.command
@lb.add_checks(lb.owner_only)
@lb.command("kms", "Kill the bot", aliases=["shutdown"])
@lb.implements(lb.PrefixCommand)
async def shutdown(ctx: lb.Context) -> None:
    await ctx.respond("Shutting bot down...")
    await ctx.bot.close()


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(walkthrough)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(walkthrough)
