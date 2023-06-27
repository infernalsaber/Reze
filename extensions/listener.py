import re
import requests
from datetime import datetime
import asyncio
import os

from PIL import Image
import io

import lightbulb as lb
import hikari as hk
import miru
from miru.ext import nav


from extensions.dir import GenericButton
from extPlugins.misc import requestsFailedError

"""
#TODO
1. Change the resolution of images gotten for preview (check: shorturl.at/qwHV6)✅
2. Make it refer to the original message (info embed)🌊
3. Custom navigator buttons (inc. kill button) 〰
"""

al_listener = lb.Plugin(
    "Weeb", "Search functions for anime, manga and characters (with an easter egg)"
)

regex = r"\b(https?:\/\/)?(www.)?anilist.co\/(anime|manga)\/(\d{1,6})"
pattern = re.compile(regex)


async def getImpInfo(chapters):
    volumeLast = list(chapters["volumes"].keys())[0]
    chapterLast = list(chapters["volumes"][volumeLast]["chapters"].keys())[0]
    idLast = chapters["volumes"][volumeLast]["chapters"][chapterLast]["id"]

    volumeFirst = list(chapters["volumes"].keys())[-1]
    chapterFirst = list(chapters["volumes"][volumeFirst]["chapters"].keys())[-1]
    idFirst = chapters["volumes"][volumeFirst]["chapters"][chapterFirst]["id"]

    return {
        "latest": {"chapter": chapterLast, "id": idLast},
        "first": {"chapter": chapterFirst, "id": idFirst},
    }


# @al_listener.listener(hk.th)


@al_listener.listener(hk.GuildMessageCreateEvent)
async def al_link_finder(event: hk.GuildMessageCreateEvent) -> None:
    if event.is_bot:
        return
    # print(event.message.content)
    listOfSeries = pattern.findall(event.message.content) or []
    # a = hk.MessageFlag
    # print(listOfSeries)
    if len(listOfSeries) != 0:
        await event.message.respond("Beep, bop. AniList link found")
        await al_listener.bot.rest.edit_message(
            event.channel_id, event.message, flags=hk.MessageFlag.SUPPRESS_EMBEDS
        )

        for series in listOfSeries:
            # print(series)
            query = """
query ($id: Int, $search: String, $type: MediaType) { # Define which variables will be used in the query (id)
  Media (id: $id, search: $search, type: $type, sort: POPULARITY_DESC) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
    id
    idMal
    title {
        english
        romaji
    }
    type
    averageScore
    format
    meanScore
    chapters
    episodes
    startDate {
        year
    }
    coverImage {
        large
    }
    bannerImage
    genres
    status
    description (asHtml: false)
    siteUrl
  }
}

"""

            variables = {"id": series[3], "type": series[2].upper()}

            response = requests.post(
                "https://graphql.anilist.co",
                json={"query": query, "variables": variables},
            )
            if response.status_code != 200:
                print(response.json())
                await event.message.respond(
                    f"Nvm 😵, error `code: {response.status_code}`"
                )
                return
            response = response.json()["data"]["Media"]

            title = response["title"]["english"] or response["title"]["romaji"]

            no_of_items = response["chapters"] or response["episodes"] or "NA"

            await event.message.respond(
                content="Here are it's details",
                embed=hk.Embed(
                    description="\n\n",
                    color=0x2B2D42,
                    timestamp=datetime.now().astimezone(),
                )
                .add_field("Rating", response["averageScore"])
                .add_field("Genres", ",".join(response["genres"]))
                .add_field("Status", response["status"], inline=True)
                .add_field(
                    "Chapters" if response["type"] == "MANGA" else "ANIME",
                    no_of_items,
                    inline=True,
                )
                .add_field(
                    "Summary",
                    f"{response['description'][0:250].replace('<br>', '') if len(response['description']) > 250 else response['description'].replace('<br>', '')}...",
                )
                .set_thumbnail(response["coverImage"]["large"])
                .set_image(response["bannerImage"])
                .set_author(url=response["siteUrl"], name=title)
                .set_footer(
                    text="Source: AniList",
                    icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
                ),
            )

            # await al_search(ctx, type, media)


# @al_listener.listener(hk.GuildReactionAddEvent)
# async def pinner(event: hk.GuildReactionAddEvent) -> None:
#     ...
@al_listener.command
@lb.option(
    "media",
    "The name of the media to search",
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.option(
    "type", "The type of media to search for", choices=["anime", "manga", "character"]
)
@lb.command(
    "lookup",
    "Look up anime/manga on anilist",
    pass_options=True,
    aliases=["lu"],
    auto_defer=True,
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def al_search(ctx: lb.Context, type: str, media: str) -> None:
    query = """
query ($id: Int, $search: String, $type: MediaType) { # Define which variables will be used in the query (id)
  Media (id: $id, search: $search, type: $type, sort: POPULARITY_DESC) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
    id
    idMal
    title {
        english
        romaji
    }
    type
    averageScore
    format
    meanScore
    chapters
    episodes
    startDate {
        year
    }
    coverImage {
        large
    }
    bannerImage
    genres
    status
    description (asHtml: false)
    siteUrl
  }
}

"""
    if type.lower() in ["anime", "manga", "m", "a"]:
        if type[0].lower() == "m":
            type = "MANGA"
        else:
            type = "ANIME"
    elif type in ["character", "c"]:
        # pass
        await search_character(ctx, media)
        return
    else:
        await ctx.respond("Invalid media type. Please use anime(a) or manga(m)")
        return

    variables = {"search": media, "type": type}

    response = requests.post(
        "https://graphql.anilist.co", json={"query": query, "variables": variables}
    )
    if response.status_code != 200:
        print(response.json())
        await ctx.respond(
            f"Failed to fetch data 😵, error `code: {response.status_code}`"
        )
        return
    response = response.json()["data"]["Media"]

    title = response["title"]["english"] or response["title"]["romaji"]

    no_of_items = response["chapters"] or response["episodes"] or "NA"

    if response["description"]:
        response["description"] = (
            response["description"]
            .replace("<br>", "")
            .replace("<i>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("</i>", "")
        )
        if len(response["description"]) > 250:
            response["description"] = f"{response['description'][0:250]}..."
    else:
        response["description"] = "NA"

    if type == "ANIME":
        await ctx.respond(
            embed=hk.Embed(
                description="\n\n",
                color=0x2B2D42,
                timestamp=datetime.now().astimezone(),
            )
            .add_field("Rating", response["averageScore"])
            .add_field("Genres", ",".join(response["genres"]))
            .add_field("Status", response["status"], inline=True)
            .add_field("Episodes", no_of_items, inline=True)
            .add_field("Summary", response["description"])
            .set_thumbnail(response["coverImage"]["large"])
            .set_image(response["bannerImage"])
            .set_author(url=response["siteUrl"], name=title)
            .set_footer(
                text="Source: AniList",
                icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
            )
        )
        return

    elif type == "character":
        await search_character(ctx, media)
        return

    # if response['format'] == 'MANGA':
    print("\n\nUsing MD\n\n")
    base_url = "https://api.mangadex.org"

    r = requests.get(f"{base_url}/manga", params={"title": title})

    manga_id = r.json()["data"][0]["id"]

    # print(f"The link to the manga is: https://mangadex.org/title/{manga_id}")

    languages = ["en"]

    r = requests.get(
        f"{base_url}/manga/{manga_id}/aggregate",
        params={"translatedLanguage[]": languages},
    )
    # print(r.status_code)
    # print(r.json())
    # print([chapter["id"] for chapter in r.json()["data"]])
    data = await getImpInfo(r.json())

    if no_of_items == "NA":
        no_of_items = f"[{data['latest']['chapter'].split('.')[0]}](https://cubari.moe/read/mangadex/{manga_id})"
    else:
        no_of_items = f"[{no_of_items}](https://cubari.moe/read/mangadex/{manga_id})"

    view = miru.View()
    view.add_item(
        GenericButton(
            style=hk.ButtonStyle.SECONDARY,
            label="Preview",
            emoji=hk.Emoji.parse("<a:peek:1061709886712455308>"),
        )
    )

    preview = await ctx.respond(
        embed=hk.Embed(
            description="\n\n", color=0x2B2D42, timestamp=datetime.now().astimezone()
        )
        .add_field("Rating", response["averageScore"])
        .add_field("Genres", ",".join(response["genres"]))
        .add_field("Status", response["status"], inline=True)
        .add_field(
            "Chapters" if response["type"] == "MANGA" else "Episodes",
            no_of_items,
            inline=True,
        )
        .add_field("Summary", response["description"])
        .set_thumbnail(response["coverImage"]["large"])
        .set_image(response["bannerImage"])
        .set_author(url=response["siteUrl"], name=title)
        .set_footer(
            text="Source: AniList",
            icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
        ),
        components=view,
    )
    # return
    await view.start(preview)
    await view.wait()
    msg = ctx.previous_response.message
    # al_listener.bot.rest.create_message(channel)
    if hasattr(view, "answer"):
        await ctx.respond(
            f"Loading chapter {hk.Emoji.parse('<a:loading_:1061933696648740945>')}",
            reply=True,
        )
        print(f"\n\n{view.answer}\n\n")
    else:
        await ctx.edit_last_response(components=[])
        return

    data["first"]["id"]

    r = requests.get(f"{base_url}/at-home/server/{data['first']['id']}")
    if not r.ok:
        raise requestsFailedError
        return
    r_json = r.json()
    pages = []
    # req = requests.Session()
    # try:

    # os.makedirs(f"./manga/{data['first']['id']}")
    # from pprint import pprint
    # pprint(r_json)
    for i, page in enumerate(r_json["chapter"]["data"]):
        # print(f"\n\n{r_json['baseUrl']}/data/{r_json['chapter']['hash']}/{page}\n\n")
        # pageResp = req.get(f"{r_json['baseUrl']}/data/{r_json['chapter']['hash']}/{page}")

        # if pageResp.ok:
        # img = Image.open(io.BytesIO(pageResp.content))
        # img.resize(tuple(int(0.90*i) for i in img.size), Image.LANCZOS).save(f"./manga/{data['first']['id']}/pilsave_qty95_size90.png", quality=95, optimize=True)
        # with open(f"./manga/{data['first']['id']}/io.png", mode="wb") as f:
        #     f.write(pageResp.content)
        # Image.open(io.BytesIO(pageResp.content)).save(f"./manga/{data['first']['id']}/pilsave.png")
        # Image.open(io.BytesIO(pageResp.content)).convert("RGB").save(f"./manga/{data['first']['id']}/{i}.jpg")
        # img = Image.open(io.BytesIO(pageResp.content))
        # img.resize(tuple(int(0.60*i) for i in img.size), Image.LANCZOS).save(f"./manga/{data['first']['id']}/pilsave_qty90_size75.png", quality=75, optimize=True)
        # return
        # else:
        #     print(pageResp.content)
        #     os.rmdir(f"./manga/{data['first']['id']}")
        #     raise requestFailedError
        #     return

        # except FileExistsError:
        #     print("\n\nThis series exists\n\n")
        # await asyncio.sleep(1)

        # asyncio.sleep(3)
        # for item in sorted(os.listdir(f"./manga/{data['first']['id']}")):
        # await ctx.respond(embed=hk.Embed().set_image(f"./manga/{data['first']['id']}/{item}")) WORKS, but meh
        # await ctx.respond(embed=hk.Embed(description="dash"), attachment=f"./manga/{data['first']['id']}/{item}") IT WORKS but no navi
        pages.append(
            hk.Embed(title=title, color=0xFF6740)
            .set_image(f"{r_json['baseUrl']}/data/{r_json['chapter']['hash']}/{page}")
            .set_footer(
                "Fetched via: MangaDex",
                icon="https://avatars.githubusercontent.com/u/100574686?s=280&v=4",
            )
        )
    pages.append(
        hk.Embed(title=title, url=f"https://cubari.moe/read/mangadex/{manga_id}/2/1")
        .set_image(response["coverImage"]["large"])
        .set_author(
            name="Click here to continue reading",
            url=f"https://cubari.moe/read/mangadex/{manga_id}/2/1",
        )
    )
    buttons = [
        nav.PrevButton(
            style=hk.ButtonStyle.SECONDARY,
            emoji=hk.Emoji.parse("<:pink_arrow_left:1059905106075725955>"),
        ),
        nav.IndicatorButton(),
        nav.NextButton(
            style=hk.ButtonStyle.SECONDARY,
            emoji=hk.Emoji.parse("<:pink_arrow_right:1059900771816189953>"),
        ),
    ]
    await ctx.delete_last_response()
    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    # print("Time is ", time.time()-timeInit)
    await navigator.send(ctx.channel_id, responded=True)


# class requestFailedError(Exception):
#     pass


async def search_animanga(ctx: lb.Context, type: str, media: str):
    t1 = datetime.now().timestamp()

    query = """
query ($id: Int, $search: String, $type: MediaType) { # Define which variables will be used in the query (id)
  Media (id: $id, search: $search, type: $type, sort: POPULARITY_DESC) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
    id
    idMal
    title {
        english
        romaji
    }
    type
    averageScore
    format
    meanScore
    chapters
    episodes
    startDate {
        year
    }
    coverImage {
        large
    }
    bannerImage
    genres
    status
    description (asHtml: false)
    siteUrl
  }
}

"""

    variables = {"search": media, "type": type}

    response = await ctx.bot.d.aio_session.post(
        "https://graphql.anilist.co", json={"query": query, "variables": variables}
    )
    if not response.ok:
        print(await response.json())
        await ctx.respond(
            f"Failed to fetch data 😵, error `code: {response.status_code}`"
        )
        return
    response = await response.json()
    response = response["data"]["Media"]

    title = response["title"]["english"] or response["title"]["romaji"]

    no_of_items = response["chapters"] or response["episodes"] or "NA"

    if response["description"]:
        response["description"] = (
            response["description"]
            .replace("<br>", "")
            .replace("<i>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("</i>", "")
        )
        if len(response["description"]) > 250:
            response["description"] = f"{response['description'][0:250]}..."
    else:
        response["description"] = "NA"

    if type == "ANIME":
        await ctx.respond(
            embed=hk.Embed(
                description="\n\n",
                color=0x2B2D42,
                timestamp=datetime.now().astimezone(),
            )
            .add_field("Rating", response["averageScore"])
            .add_field("Genres", ",".join(response["genres"]))
            .add_field("Status", response["status"], inline=True)
            .add_field("Episodes", no_of_items, inline=True)
            .add_field("Summary", response["description"])
            .set_thumbnail(response["coverImage"]["large"])
            .set_image(response["bannerImage"])
            .set_author(url=response["siteUrl"], name=title)
            .set_footer(
                text="Source: AniList",
                icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
            )
        )
        return

    print("\n\nUsing MD\n\n")
    base_url = "https://api.mangadex.org"

    r = await ctx.bot.d.aio_session.get(f"{base_url}/manga", params={"title": title})
    r = await r.json()

    manga_id = r["data"][0]["id"]
    languages = ["en"]
    r = await ctx.bot.d.aio_session.get(
        f"{base_url}/manga/{manga_id}/aggregate",
        params={"translatedLanguage[]": languages},
    )

    data = await getImpInfo(await r.json())

    if no_of_items == "NA":
        no_of_items = f"[{data['latest']['chapter'].split('.')[0]}](https://cubari.moe/read/mangadex/{manga_id})"
    else:
        no_of_items = f"[{no_of_items}](https://cubari.moe/read/mangadex/{manga_id})"

    view = miru.View()
    view.add_item(
        GenericButton(
            style=hk.ButtonStyle.SECONDARY,
            label="Preview",
            emoji=hk.Emoji.parse("<a:peek:1061709886712455308>"),
        )
    )

    preview = await ctx.respond(
        embed=hk.Embed(
            description="\n\n", color=0x2B2D42, timestamp=datetime.now().astimezone()
        )
        .add_field("Rating", response["averageScore"])
        .add_field("Genres", ",".join(response["genres"]))
        .add_field("Status", response["status"], inline=True)
        .add_field(
            "Chapters" if response["type"] == "MANGA" else "Episodes",
            no_of_items,
            inline=True,
        )
        .add_field("Summary", response["description"])
        .set_thumbnail(response["coverImage"]["large"])
        .set_image(response["bannerImage"])
        .set_author(url=response["siteUrl"], name=title)
        .set_footer(
            text="Source: AniList",
            icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
        ),
        components=view,
    )
    print("\n\nTime is ", datetime.now().timestamp() - t1, "s\n\n")

    await view.start(preview)
    await view.wait()

    if hasattr(view, "answer"):
        await ctx.respond(
            f"Loading chapter {hk.Emoji.parse('<a:loading_:1061933696648740945>')}",
            reply=True,
            mentions_everyone=True,
        )
        print(f"\n\n{view.answer}\n\n")
    else:
        await ctx.edit_last_response(components=[])
        return

    data["first"]["id"]

    r = requests.get(f"{base_url}/at-home/server/{data['first']['id']}")
    if not r.ok:
        raise requestsFailedError
        return
    r_json = r.json()
    pages = []

    for i, page in enumerate(r_json["chapter"]["data"]):
        pages.append(
            hk.Embed(title=title, color=0xFF6740)
            .set_image(f"{r_json['baseUrl']}/data/{r_json['chapter']['hash']}/{page}")
            .set_footer(
                "Fetched via: MangaDex",
                icon="https://avatars.githubusercontent.com/u/100574686?s=280&v=4",
            )
        )
    pages.append(
        hk.Embed(title=title, url=f"https://cubari.moe/read/mangadex/{manga_id}/2/1")
        .set_image(response["coverImage"]["large"])
        .set_author(
            name="Click here to continue reading",
            url=f"https://cubari.moe/read/mangadex/{manga_id}/2/1",
        )
    )
    buttons = [
        nav.PrevButton(
            style=hk.ButtonStyle.SECONDARY,
            emoji=hk.Emoji.parse("<:pink_arrow_left:1059905106075725955>"),
        ),
        nav.IndicatorButton(),
        nav.NextButton(
            style=hk.ButtonStyle.SECONDARY,
            emoji=hk.Emoji.parse("<:pink_arrow_right:1059900771816189953>"),
        ),
    ]
    await ctx.delete_last_response()
    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    await navigator.send(ctx.channel_id, responded=True)


@al_listener.command
@lb.command("Look up manga", "Search a manga")
@lb.implements(lb.MessageCommand)
async def mangamenu(ctx: lb.MessageContext):
    await search_animanga(ctx, "MANGA", ctx.options["target"].content)


@al_listener.command
@lb.command("Look up anime", "Search an anime")
@lb.implements(lb.MessageCommand)
async def animemenu(ctx: lb.MessageContext):
    await search_animanga(ctx, "ANIME", ctx.options["target"].content)


@al_listener.command
@lb.option("filter", "Filter the type of anime to fetch", required=False)
@lb.command("top", "Find top anime on MAL", pass_options=True)
@lb.implements(lb.PrefixCommand)
async def topanime(ctx: lb.PrefixContext, filter: str = None):
    if filter and filter in ["airing", "upcoming", "bypopularity", "favorite"]:
        num = 10
    else:
        num = 5
        filter = "anime"

    async with ctx.bot.d.aio_session.get(
        "https://api.jikan.moe/v4/top/anime", params=dict(limit=num, filter=filter)
    ) as res:
        if res.ok:
            res = await res.json()
            embed = (
                hk.Embed(color=0x2E51A2)
                .set_author(name="Top Anime")
                .set_footer(
                    "Fetched via MyAnimeList.net",
                    icon="https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAiC8a86sHufn_jOI-JGtoCQ",
                )
            )

            for i, item in enumerate(res["data"]):
                embed.add_field(
                    f"{i+1}.",
                    f"```ansi\n\u001b[0;32m{item['rank'] or ''}. \u001b[0;36m{item['title']} \u001b[0;33m({item['score'] or item['members']})```",
                )

            await ctx.respond(embed=embed)
        else:
            raise requestsFailedError
            return


# @al_listener.command
# @lb.command("navi", "navi")
# @lb.implements(lb.PrefixCommand)
# async def navi_check(ctx: lb.PrefixContext):
#     pages = []
#     pages.append(
#         hk.Embed(
#             title="Link Image"
#         )
#         .set_image("https://ichef.bbci.co.uk/news/976/cpsprodpb/16620/production/_91408619_55df76d5-2245-41c1-8031-07a4da3f313f.jpg")
#     )
#     pages.append(
#         hk.Embed(
#             title="Local Image"
#         )
#         .set_image("./pictures/bocchi.png")
#     )
#     pages.append(
#         hk.Embed(
#             title="Link Image2"
#         )
#         .set_image("https://whatnerd.com/wp-content/uploads/2021/02/trubbish-weird-pokemon.jpg")
#     )
#     buttons = [
#         nav.PrevButton(
#             style=hk.ButtonStyle.SECONDARY,
#             emoji=hk.Emoji.parse("<:pink_arrow_left:1059905106075725955>")
#         ),
#         nav.IndicatorButton(),
#         nav.NextButton(
#             style=hk.ButtonStyle.SECONDARY,
#             emoji=hk.Emoji.parse("<:pink_arrow_right:1059900771816189953>")
#         )
#         ]
#     navigator = nav.NavigatorView(pages=pages, buttons=buttons)
#     await navigator.send(ctx.channel_id)


@al_search.set_error_handler
async def gallery_errors_handler(event: lb.CommandErrorEvent) -> bool:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, requestFailedError):
        await event.context.respond(
            "The application failed to fetch a response", flags=hk.MessageFlag.EPHEMERAL
        )

    return False


async def search_character(ctx: lb.Context, character: str):
    query = """
query ($id: Int, $search: String) { # Define which variables will be used in the query (id)
  Character (id: $id, search: $search,  sort: FAVOURITES_DESC) { # Insert our variables into the query arguments (id)
    id
    name {
      full
    }
    image {
      large
    }
    gender
    dateOfBirth {
        year
        month
        day
    }
    description (asHtml: false)
    media (sort: TRENDING_DESC, perPage: 3) {
        nodes {
            title {
                romaji
                english
            }
            season
            seasonYear
            seasonInt
            episodes
            chapters
            source
            coverImage {
                large
            }
            popularity
            tags {
              name
            }
        }
    }
    favourites #♥
    siteUrl
  }
}
"""

    variables = {
        "search": character
        # ,"sort": FAVOURITES_DESC
    }

    response = await ctx.bot.d.aio_session.post(
        "https://graphql.anilist.co", json={"query": query, "variables": variables}
    )
    if not response.ok:
        # if response.status_code != 200:
        print(await response.json())
        await ctx.respond(
            f"Failed to fetch data 😵, error `code: {response.status_code}`"
        )
        return
    response = await response.json()
    response = response["data"]["Character"]

    title = response["name"]["full"]

    if response["dateOfBirth"]["month"] and response["dateOfBirth"]["day"]:
        dob = f"{response['dateOfBirth']['day']}/{response['dateOfBirth']['month']}"
        if response["dateOfBirth"]["year"]:
            dob += f"/{response['dateOfBirth']['year']}"
    else:
        dob = "NA"

    # no_of_items = response['chapters'] or response['episodes'] or "NA"

    if response["description"]:
        response["description"] = (
            response["description"]
            .replace("<br>", "")
            .replace("~!", "||")
            .replace("!~", "||")
        )
        if len(response["description"]) > 400:
            response["description"] = f"{response['description'][0:400]}..."
    else:
        response["description"] = "NA"

    await ctx.respond(
        embed=hk.Embed(
            description="\n\n", color=0x2B2D42, timestamp=datetime.now().astimezone()
        )
        .add_field("Gender", response["gender"])
        .add_field("DOB", dob, inline=True)
        .add_field("Favourites", f"{response['favourites']}❤", inline=True)
        .add_field("Character Description", response["description"])
        .set_thumbnail(response["image"]["large"])
        .set_author(url=response["siteUrl"], name=title)
        .set_footer(
            text="Source: AniList",
            icon="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/AniList_logo.svg/1024px-AniList_logo.svg.png",
        )
    )
    return


@al_listener.command
@lb.option("character", "character")
@lb.command("luc", "Search a chara", pass_options=True)
@lb.implements(lb.PrefixCommand)
async def chara(ctx: lb.PrefixContext, character: str):
    await search_character(ctx, character)


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(al_listener)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(al_listener)
