"""
This is the module to make 3x3s or find Google Image results
"""
import re
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image

import hikari as hk
import lightbulb as lb
import miru
from miru.ext import nav

from extPlugins.misc import CustomPrevButton, CustomNextButton

gallery_plugin = lb.Plugin("Gallery", "Get a gallery or a collage of images")

# TODO
# 1. Button Styles, make them look less bad✅
# 2. 3x3 ✅


def original_images(soup):
    googleImages = []

    all_script_tags = soup.select("script")

    matched_images_data = "".join(
        re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags))
    )

    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_image_data = re.findall(
        r"\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}", matched_images_data_json
    )

    matched_google_image_thumbnails = ", ".join(
        re.findall(
            r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
            str(matched_google_image_data),
        )
    ).split(", ")

    thumbnails = [
        bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode escape"
        )
        for thumbnail in matched_google_image_thumbnails
    ]

    removed_matched_google_images_thumbnails = re.sub(
        r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
        "",
        str(matched_google_image_data),
    )

    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails,
    )

    full_res_images = [
        bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode-escape"
        )
        for img in matched_google_full_resolution_images
    ]
    # print("Parsing shit")
    # print(full_res_images[0:2])
    for index, (metadata, thumbnail, original) in enumerate(
        zip(soup.select(".isv-r.PNCib.MSM1fd.BUooTd"), thumbnails, full_res_images),
        start=1,
    ):
        try:
            google_images.append(
                {
                    "title": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                        "title"
                    ],
                    "link": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                        "href"
                    ],
                    "source": metadata.select_one(".fxgdke").text,
                    "thumbnail": thumbnail,
                    "original": original,
                }
            )
        except Exception as e:
            print("Google is shit")
            google_images.append(
                {
                    "thumbnail": thumbnail,
                    "source": "Unknown",
                    "link": "Unknown",
                    "original": original,
                }
            )

    # print(google_images)
    return google_images


async def lookfor(query: str, num: int = 9):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    params = {
        "q": query,  # Query to search for
        "tbm": "isch",  # to display image search results
        "h1": "en",  # language for the query
        "gl": "us",  # country to fetch results from
        "ijn": "0",
    }
    # req = requests.session()
    async with gallery_plugin.bot.d.aio_session.get(
        "https://www.google.com/search", params=params, headers=headers, timeout=30
    ) as html:
        # html = req.get("https://www.google.com/search",params=params,headers=headers,timeout=30)
        # print("Fetched g search")
        soup = BeautifulSoup(await html.text(), "lxml")
    return original_images(soup)[:num]


class MyNavButton(nav.NavButton):
    async def callback(self, ctx: miru.ViewContext) -> None:
        await ctx.respond("Clicked", flags=hk.MessageFlag.EPHEMERAL)

    async def before_page_change(self) -> None:
        self.label = f"Page: {self.view.current_page+1}"


# import time


@gallery_plugin.command
@lb.option(
    "query",
    "The query whose gallery to generate",
    str,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.command("gallery", "Generate a gallery of a particular item", aliases=["gi", "s"])
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def gallery(ctx: lb.Context) -> None:
    pages = []
    query = ctx.options["query"]

    response_data = await lookfor(query)
    for data in response_data:
        pages.append(
            hk.Embed()
            .set_image(data["original"])
            .set_footer(f"Source: {data['source']}")
        )

    buttons = [CustomPrevButton(), nav.IndicatorButton(), CustomNextButton()]

    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    # print("Time is ", time.time()-timeInit)
    await navigator.send(ctx.channel_id)


@gallery_plugin.command
@lb.command("Generate Image Gallery", "Find images of the target")
@lb.implements(lb.MessageCommand)
async def img_gallery_menu(ctx: lb.MessageContext):
    pages = []
    query = ctx.options["target"].content

    response_data = await lookfor(query)
    for data in response_data:
        pages.append(
            hk.Embed()
            .set_image(data["original"])
            .set_footer(f"Source: {data['source']}")
        )

    buttons = [CustomPrevButton(), nav.IndicatorButton(), CustomNextButton()]

    navigator = nav.NavigatorView(pages=pages, buttons=buttons)
    await navigator.send(ctx.channel_id)


@gallery_plugin.command
@lb.option(
    "values",
    "The values to put in the 3x3",
    str,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.command(
    "3x3",
    "Generate a gallery of a particular item",
    aliases=["make3x3"],
    pass_options=True,
)
@lb.implements(lb.PrefixCommand)
async def collage(ctx: lb.Context, values: str) -> None:
    temp = values.split("add=")
    if len(temp) == 2:
        values, add = temp
    else:
        add = ""
    values = values.split(",")
    images = []
    import io

    for value in values:
        async with ctx.bot.d.aio_session.get(
            (await lookfor(f"{value} {add}"))[0]["original"]
        ) as resp:
            images.append(Image.open(io.BytesIO(await resp.read())))

    _3x3 = Image.new("RGBA", (900, 900), (255, 255, 255, 0))

    for i, img in enumerate(images):
        if i > 9:
            await ctx.respond("Too many arguments")
            return

        x = (i % 3) * 300
        y = int(i / 3) * 300

        width, height = img.size
        img = img.crop(
            (0, 0, width, width) if height > width else (0, 0, height, height)
        ).resize((300, 300))

        _3x3.paste(img, (x, y))

    _3x3.save(f"pictures/3x3{ctx.author.username}.png")
    await ctx.respond(
        f"Here's your 3x3 {ctx.user.mention}",
        attachment=f"pictures/3x3{ctx.author.username}.png",
        user_mentions=True,
    )


@gallery.set_error_handler
async def gallery_errors_handler(event: lb.CommandErrorEvent) -> bool:
    # exception = event.exception.__cause__ or event.exception

    # if isinstance(exception, lb.MissingRequiredPermission):
    #     await event.context.respond("You're missing some perms there, bub.")
    #     return True

    return False


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(gallery_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(gallery_plugin)
