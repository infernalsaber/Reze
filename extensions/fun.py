import hikari as hk
import lightbulb as lb
import miru
from miru.ext import nav

from datetime import datetime
import os

import requests
import random
import re

from extPlugins.misc import requestsFailedError
from extPlugins.misc import CustomPrevButton, CustomNextButton

import dotenv

dotenv.load_dotenv()

DB_KEY = os.getenv("DANBOORU_KEY")
DB_ID = os.getenv("DANBOORU_USER")

fun_plugin = lb.Plugin("Fun", "Misc. commands serving no real purpose")

import user_agent


@fun_plugin.command
@lb.command("fun", "entertainment", aliases=["f"])
@lb.implements(lb.PrefixCommandGroup, lb.SlashCommandGroup)
async def fun_group(ctx: lb.Context) -> None:
    pass


@fun_group.child
@lb.command("meme", "Fetch meme")
@lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
async def meme_subcommand(ctx: lb.Context) -> None:
    async with ctx.bot.d.aio_session.get("https://meme-api.com/gimme") as response:
        res = await response.json()
        if response.ok and res["nsfw"] != True:
            embed = (
                hk.Embed(color=0xF4EAE9)  # ,timestamp=datetime.now().astimezone()
                .set_author(name=f"{res['title']} ({res['ups']}🔼)", url=res["postLink"])
                .set_image(res["url"])
                .set_footer(
                    text=f"Posted by: {res['author']} in r/{res['subreddit']}",
                    icon="https://external-preview.redd.it/iDdntscPf-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?width=640&crop=smart&auto=webp&s=bfd318557bf2a5b3602367c9c4d9cd84d917ccd5",
                )
            )
            await ctx.respond(embed)
        else:
            try:
                code = response.status
            except:
                code = 404
            await ctx.respond(
                f"No meme was fetched 😖 `code: {response.status}`",
                flags=hk.MessageFlag.EPHERMAL,
            )


class AnimalView(miru.View):
    def __init__(self, author: hk.User) -> None:
        self.author = author
        super().__init__(timeout=60)

    @miru.text_select(
        custom_id="animal_select",
        placeholder="Pick an animal",
        options=[
            miru.SelectOption("Dog", value="dog", emoji="🐶"),
            miru.SelectOption("Bird", value="bird", emoji="🐦"),
            miru.SelectOption("Koala", value="koala", emoji="🐨"),
            miru.SelectOption("Panda", value="panda", emoji="🐼"),
            miru.SelectOption("Cat", value="cat", emoji="🐱"),
            miru.SelectOption("Racoon", value="racoon", emoji="🦝"),
            miru.SelectOption(
                "Red Panda",
                value="red_panda",
                emoji=hk.Emoji.parse("<:RedPanda:1060649685934674001>"),
            ),
        ],
    )
    async def select_menu(self, select: miru.TextSelect, ctx: miru.Context) -> None:
        print(select)
        animal = select.values[0]
        async with ctx.bot.d.aio_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if res.ok:
                res = await res.json()

                await ctx.edit_response(
                    f"Here's a {animal.replace('_', ' ')} for you!!",
                    components=[],
                    embed=hk.Embed(
                        title="",
                        description=res["fact"],
                        color=0xF4EAE9,
                        timestamp=datetime.now().astimezone(),
                    )
                    .set_image(res["image"])
                    .set_footer(
                        f"Requested by: {ctx.author}", icon=ctx.author.avatar_url
                    ),
                )
            else:
                await ctx.edit_response(
                    f"API error, `code:{res.status}`", components=[]
                )

    async def on_timeout(self) -> None:
        await self.message.edit("Timed out", components=[])

    async def view_check(self, ctx: miru.Context) -> bool:
        return ctx.user.id == self.author.id


@fun_group.child
@lb.command("animal2", "get an animaru uwu")
@lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
async def give_animal(ctx: lb.Context) -> None:
    view = AnimalView(ctx.author)
    resp = await ctx.respond("Pick an animal", components=view.build())
    msg = await resp.message()
    await view.start(msg)
    await view.wait()
    # ctx.get_channel().pin


@fun_group.child
@lb.command("joke", "Fetch some joks")
@lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
async def joke_reddit(ctx: lb.Context) -> None:
    reddit = ctx.bot.d.reddit
    print(reddit.read_only)
    subreddit = await reddit.subreddit("jokes+dadjokes")
    submissions = subreddit.hot(limit=50)
    # sr, sr_img = submissions.name, submissions.icon_img

    flag = True
    count = 0
    while flag:
        randomint = random.randint(0, 50)
        async for submission in submissions:
            # if count == randomint:
            if count == randomint and submission.selftext != r"\[removed\]":
                # submission = submissions[randomint]
                await ctx.respond(
                    embed=hk.Embed(
                        description=submission.selftext,
                        timestamp=datetime.fromtimestamp(
                            int(submission.created_utc)
                        ).astimezone(),
                        color=0xF4EAE9,
                    )
                    .set_author(name=submission.title, url=submission.url)
                    .set_footer(
                        f"Posted by: {submission.author}",
                        icon="https://icons.iconarchive.com/icons/limav/flat-gradient-social/512/Reddit-icon.png",
                    )
                )
                flag = False
                break
            count = count + 1
    await reddit.close()


@fun_plugin.command
@lb.option("subreddit", "Name of the subreddit")
@lb.command(
    "subreddit", "Fetch a hot post from a subreddit", pass_options=True, aliases=["sr"]
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def subreddit(ctx: lb.Context, subreddit: str) -> None:
    reddit = ctx.bot.d.reddit
    print(reddit.read_only)
    subreddit = await reddit.subreddit(subreddit)
    submissions = subreddit.hot(limit=10)
    # sr, sr_img = submissions.name, submissions.icon_img

    flag = True
    count = 0
    while flag:
        randomint = random.randint(0, 10)
        async for submission in submissions:
            # if count == randomint:
            if count == randomint and submission.selftext != r"\[removed\]":
                # submission = submissions[randomint]
                await ctx.respond(
                    embed=hk.Embed(
                        description=submission.selftext,
                        timestamp=datetime.fromtimestamp(
                            int(submission.created_utc)
                        ).astimezone(),
                        color=0xF4EAE9,
                    )
                    .set_author(
                        name=f"{submission.title} {submission.score}⬆, {int(submission.score*(1/submission.upvote_ratio-1))}⬇",
                        url=submission.url,
                    )
                    .set_image(submission.url)
                    .set_footer(
                        f"Posted by: {submission.author}",
                        icon="https://icons.iconarchive.com/icons/limav/flat-gradient-social/512/Reddit-icon.png",
                    )
                )
                flag = False
                break
            count = count + 1


@fun_plugin.command
@lb.option("number", "Number of posts to be fetched", int, required=False)
@lb.option("tags", "Tags of the posts to be fetched", str, required=False)
@lb.command(
    "danbooru", "Fetch some arts from danbooru", pass_options=True, aliases=["db"]
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def danbooru(ctx: lb.Context, tags: str, number: int = None) -> None:
    url = "https://danbooru.donmai.us/"
    headers = {"User-Agent": user_agent.generate_user_agent()}
    if number and number > 30:
        await ctx.respond("Too many requests")
        return

    if not number:
        number = 10

    page = random.randint(1, 5)

    if not tags:
        response = requests.get(
            f"{url}/posts.json",
            params=dict(limit=number + 5, api_key=DB_KEY, login=DB_ID, page=page),
            headers=headers,
        )
    else:
        # response = requests.get(f"{url}/posts.json", params=dict(limit=number+5, tags=f"{tags}", api_key=DB_KEY, login=DB_ID, page=page), headers=headers)
        response = requests.get(
            f"{url}/posts.json?limit={number+5}&tags={tags}&api_key={DB_KEY}&login={DB_ID}&page={page} ",
            headers=headers,
        )
    if not response.ok:
        print(response.content)
        raise requestsFailedError
        return

    pages = []

    userName = re.compile(r"https?://twitter.com/(\w+)/status/\w+")
    # from pprint import pprint
    # pprint(response.json())
    # print("\n\n", number, "\n\n")

    for item in response.json():
        if item["pixiv_id"]:
            source = f"{item['pixiv_id']} on Pixiv"
            icon = "https://w7.pngwing.com/pngs/952/504/png-transparent-pixiv-graphic-designer-illustrator-design-blue-text-logo.png"
        elif userName.search(item["source"]):
            source = f"{userName.search(item['source']).group(1)} on Twitter"
            icon = "https://static.vecteezy.com/system/resources/previews/002/534/045/original/social-media-twitter-logo-blue-isolated-free-vector.jpg"
        else:
            source = "Unknown"
            icon = None
        print(item.keys())
        if not "file_url" in item.keys():
            pass
        else:
            # if not item["large_file_url"]:
            pages.append(
                hk.Embed()
                .set_image(item["file_url"])
                .set_footer(f"Source: {source}", icon=icon)
            )
            if len(pages) == number:
                break

    buttons = [CustomPrevButton(), nav.IndicatorButton(), CustomNextButton()]

    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    await navigator.send(ctx.channel_id)


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(fun_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(fun_plugin)
