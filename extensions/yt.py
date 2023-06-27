from typing import Optional
from PIL import Image
import datetime
import re
from dataclasses import replace
import requests
import os

import hikari as hk
import lightbulb as lb
import miru

import isodate
import dotenv


# Custom plugin
from extPlugins.download_vid import downloadVideo
from extPlugins.misc import get_dominant_colour

from extensions.dir import KillButton, GenericButton

dotenv.load_dotenv()

YT_KEY = os.environ["yt_key"]

"""
#TODO
1. Add kill butttons on -yts views ✅
2. Add back button on the second view of -yts
3. Remove view on timeout
"""


class YTVideo:
    def __init__(self, searchResults: dict, i: int) -> None:
        self.vName: str = searchResults["items"][i]["snippet"]["title"]
        self.vId: str = searchResults["items"][i]["id"]["videoId"]
        self.vThumb: str = searchResults["items"][i]["snippet"]["thumbnails"]["high"][
            "url"
        ]  # make it medium later
        self.vChannel: str = searchResults["items"][i]["snippet"]["channelTitle"]
        # pprint(searchResults["items"][i])

    def get_link(self) -> str:
        return f"https://www.youtube.com/watch?v={self.vId}"

    def set_duration(self, req) -> str:
        ytapi2 = req.get(
            f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={self.vId}&regionCode=US&key={YT_KEY}"
        )
        ytapi2 = ytapi2.json()
        self.vDuration = str(
            isodate.parse_duration(ytapi2["items"][0]["contentDetails"]["duration"])
        )
        if self.vDuration.startswith("0:"):
            self.vDuration = str(
                isodate.parse_duration(ytapi2["items"][0]["contentDetails"]["duration"])
            )[2:]
            return self.vDuration[2:]
        return self.vDuration

    def get_duration_secs(self) -> int:
        ytapi2 = requests.get(
            f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={self.vId}&regionCode=US&key={YT_KEY}"
        )
        ytapi2 = ytapi2.json()
        return int(
            isodate.parse_duration(
                (ytapi2["items"][0]["contentDetails"]["duration"])
            ).total_seconds()
        )


# class boolButton(miru.View):
#     @miru.button(label="✅", style=hk.ButtonStyle.SUCCESS)
#     async def first(self, button: miru.Button, ctx: miru.ViewContext) -> None:
#         await ctx.respond("You clicked me!", flags=hk.MessageFlag.EPHEMERAL)

#     @miru.button(label="❌", style=hk.ButtonStyle.SECONDARY)
#     async def first(self, button: miru.Button, ctx: miru.ViewContext) -> None:
#         await ctx.respond("You clicked me!", flags=hk.MessageFlag.EPHEMERAL)


class YesButton(miru.Button):
    def __init__(self) -> None:
        # Initialize our button with some pre-defined properties
        super().__init__(style=hk.ButtonStyle.SUCCESS, label="Yes")

    # The callback is the function that gets called when the button is pressed
    # If you are subclassing, you must use the name "callback" when defining it.
    async def callback(self, ctx: miru.ViewContext) -> None:
        # You can specify the ephemeral message flag to make your response ephemeral
        # await ctx.respond("I'm sorry but this is unacceptable.", flags=hk.MessageFlag.EPHEMERAL)
        # You can access the view an item is attached to by accessing it's view property
        self.view.answer = True
        self.view.stop()


class NoButton(miru.Button):
    # Let's leave our arguments dynamic this time, instead of hard-coding them
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ViewContext) -> None:
        # await ctx.respond("This is the only correct answer.", flags=hk.MessageFlag.EPHEMERAL)
        self.view.answer = False
        self.view.stop()


class choiceButtons(miru.View):
    # def __init__(self) -> None:
    #     super.__init__(timeout=None)

    @miru.button(label="1", style=hk.ButtonStyle.SECONDARY)
    async def callback(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        await ctx.respond("You clicked me!", flags=hk.MessageFlag.EPHEMERAL)

    @miru.button(label="new button", style=hk.ButtonStyle.SUCCESS)
    async def second(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        await ctx.respond("You clicked neeww")


yt_plugin = lb.Plugin("YouTube", "Search and get songs")


@yt_plugin.command
@lb.option(
    "query", "The topic to search for", modifier=lb.commands.OptionModifier.CONSUME_REST
)
@lb.command(
    "youtubesearch", "Search YouTube and get videos", aliases=["yts"], pass_options=True
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def userinfo(ctx: lb.Context, query: str) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    req = requests.Session()
    response_params = {
        "part": "snippet",
        "maxResults": "6",
        "q": query,
        "regionCode": "US",
        "key": YT_KEY,
    }

    response = req.get(
        " https://youtube.googleapis.com/youtube/v3/search", params=response_params
    )
    # print(type(response.json()))
    if not response.ok:
        await ctx.respond(f"Error occurred 😵, code `{response.status_code}`")
        return
    embed = hk.Embed()
    lstVids = []
    embed.set_footer(f"Requested by: {ctx.author}", icon=ctx.author.avatar_url)
    view = miru.View()
    for i in range(5):
        q = YTVideo(response.json(), i)
        q.set_duration(req)
        embed.add_field(
            f"`{i+1}.`",
            f"```ansi\n\u001b[0;35m{q.vName} \u001b[0;36m[{q.vDuration[2:] if q.vDuration.startswith('0:') else q.vDuration}] ```",
        )
        lstVids.append(q)

        view.add_item(GenericButton(style=hk.ButtonStyle.SECONDARY, label=f"{i+1}"))
    view.add_item(KillButton(style=hk.ButtonStyle.DANGER, label="❌"))

    # view.add_item(NoButton(style=hk.ButtonStyle.DANGER, label="No"))
    choice = await ctx.respond(embed=embed, components=view)

    await view.start(choice)
    await view.wait()
    # view.from_message(message)
    if hasattr(view, "answer"):  # Check if there is an answer
        print(f"Received an answer! It is: {view.answer}")
    else:
        await ctx.edit_last_response("Process timed out.", embeds=[], views=[])
        return
    vidIndex = int(view.answer) - 1
    view2 = miru.View()
    view2.add_item(YesButton())
    view2.add_item(NoButton(style=hk.ButtonStyle.DANGER, label="No"))
    choice = await ctx.edit_last_response(
        embed=hk.Embed(
            title=lstVids[vidIndex].vName,
            url=lstVids[vidIndex].get_link(),
            color=hk.Color.of(
                get_dominant_colour(
                    Image.open(requests.get(lstVids[vidIndex].vThumb, stream=True).raw)
                )
            ),
            description=lstVids[vidIndex].vChannel,
        ).set_image(lstVids[vidIndex].vThumb),
        components=view2,
    )

    await view2.start(choice)
    await view2.wait()
    if hasattr(view2, "answer"):  # Check if there is an answer
        await ctx.edit_last_response(
            f"Video link: {lstVids[vidIndex].get_link()}",
            embeds=[],
            flags=hk.MessageFlag.SUPPRESS_EMBEDS,
            components=[],
        )
        if not view2.answer:
            return
    else:
        await ctx.edit_last_response("Process timed out.", embeds=[], views=[])
        return

    if len(lstVids[vidIndex].vDuration.split(":")) == 2:
        netDuration = int(lstVids[vidIndex].vDuration[0]) * 60 + int(
            lstVids[vidIndex].vDuration[1]
        )
        if not netDuration < 60 or netDuration > 501:
            print(netDuration)
            await ctx.respond("Invalid time duration.")
            return
    else:
        await ctx.respond("Invalid time duration.")
        return

    # if lstVids[vidIndex].get_duration_secs() < 60 or lstVids[vidIndex].get_duration_secs() > 601:
    #     await ctx.respond("Invalid time duration.")
    #     return
    b = await downloadVideo(lstVids[vidIndex].get_link())
    if b:
        await ctx.respond(b)
    else:
        probable_name = (
            lstVids[vidIndex]
            .vName.replace("/", "⧸")
            .replace("?", "？")
            .replace(":", "：")
            .replace("|", "｜")
            .replace("\\", "⧹")
        )
        await ctx.respond(
            content=f"{ctx.author.mention}, here's your MV",
            attachment=f"videos/{probable_name}.m4a",
            user_mentions=True,
        )


@yt_plugin.command
@lb.option("video", "The video url to download", str)
@lb.command(
    "youtubedownload", "Download a yt video", aliases=["ytdl"], pass_options=True
)
@lb.implements(lb.PrefixCommand)
async def userinfo(ctx: lb.Context, video: str) -> None:
    pattern = re.search(
        r"\b(https?://)?(www\.)?(m.)?(youtube\.com|/watch\?v=|youtu\.be/)(\w+)", video
    )
    if pattern:
        resp = requests.get(
            f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={pattern[5]}&regionCode=US&key={YT_KEY}"
        )

        if not resp.ok:
            await ctx.respond(
                f"Can't fetch video details. YT error: `{resp.status_code}`"
            )
            return

        resp = resp.json()

        duration = int(
            isodate.parse_duration(
                (resp["items"][0]["contentDetails"]["duration"])
            ).total_seconds()
        )
        if duration < 60 or duration > 501:
            await ctx.respond("Video too long")
            return

        await yt_plugin.bot.rest.edit_message(
            ctx.channel_id, ctx.event.message, flags=hk.MessageFlag.SUPPRESS_EMBEDS
        )
        await downloadVideo(video)

        probable_name = (
            resp["items"][0]["snippet"]["title"]
            .replace("/", "⧸")
            .replace("?", "？")
            .replace(":", "：")
            .replace("|", "｜")
            .replace("\\", "⧹")
        )
        await ctx.respond(
            content=f"{ctx.author.mention}, here's your MV",
            attachment=f"videos/{probable_name}.m4a",
            user_mentions=True,
        )
    else:
        if not (
            lb.checks._has_guild_permissions(ctx, perms=hk.Permissions.ADMINISTRATOR)
        ):
            await ctx.respond(
                f"That's not a YouTube video {hk.Emoji.parse('<:worry:1061307106399113216>')}"
            )
            return


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(yt_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(yt_plugin)
