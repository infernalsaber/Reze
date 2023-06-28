"""Module to do Image Transformations and Apply Effects"""
import io
import os
from typing import Optional, Sequence
import random

from PIL import Image, ImageDraw, ImageOps, ImageFont
import dotenv
import fast_colorthief

import hikari as hk
import lightbulb as lb

from extPlugins.misc import is_image


dotenv.load_dotenv()

REMOVE_BG_KEY = os.environ["removeBG_key"]


image_plugin = lb.Plugin("Image Tools", "Apply cool and useful effects to images")


# TDL
# 1. Generate palette from the given image (implement it like a card)
# 2. Filters: Blurple, Sharpen etc. + Color Visualize
# 3. Masked Wordcloud
# 4. Remove BG
# 5. Compress Image
# 6. Background Blur
# 7. Colourize(?)


async def color_palette(
    dominant_color: tuple, palette_colors: Sequence[tuple]
) -> Image.Image:
    """Generate the pillow object with the template style applied to it

    Args:
        dominant_color (tuple): The dominant colour of the original image
        palette_colors (Sequence[tuple]): The top 5 most visually present colours of the image

    Returns:
        Image.Image: Cool pillow object with the template and stuff
    """

    img_font = ImageFont.truetype("resources/fonts/TTNorms-Light.otf", size=30)
    mask = Image.new("RGBA", (960, 722), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(45, 595), (430, 645)], 30, dominant_color)
    draw.text(
        (175, 604),
        str(hk.Color.of(dominant_color).hex_code),
        fill=(255, 255, 255),
        font=img_font,
    )

    # ![pillow_composite_circle](data/dst/pillow_composite_circle.jpg)
    # mask.show()

    img = Image.open(
        f"resources/palette/{random.choice(os.listdir('resources/palette'))}"
    ).convert("RGBA")
    # img.show()
    final = Image.composite(mask, img, mask)
    # img_font = ImageFont.load_default()

    # final.show()

    for i, color in enumerate(palette_colors):
        color = hk.Color.of(color).hex_code
        mask = Image.new("RGBA", (960, 722), (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            [(496, 271 + (66 * i)), (884, 322 + (66 * i))], 30, color
        )
        draw.text(
            (625, 280 + (66 * i)), f"{color}", fill=(255, 255, 255), font=img_font
        )
        final = Image.composite(mask, final, mask)

    # mask = Image.new("RGBA", (960,722), (0,0,0,0))
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle([(496, 271), (884, 322)], 30, paletteColors[0])
    # final = Image.composite(mask, final, mask)

    # mask = Image.new("RGBA", (960,722), (0,0,0,0))
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle([(496, 334), (884, 385)], 30, paletteColors[1])
    # final = Image.composite(mask, final, mask)

    # mask = Image.new("RGBA", (960,722), (0,0,0,0))
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle([(496, 401), (884, 452)], 30, paletteColors[2])
    # final = Image.composite(mask, final, mask)

    # mask = Image.new("RGBA", (960,722), (0,0,0,0))
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle([(496, 469), (884, 520)], 30, paletteColors[3])
    # final = Image.composite(mask, final, mask)

    # mask = Image.new("RGBA", (960,722), (0,0,0,0))
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle([(496, 533), (884, 584)], 30, paletteColors[4])
    # final = Image.composite(mask, final, mask)

    return final


@image_plugin.command
@lb.command("imgtools", "Modify an image")
@lb.implements(lb.SlashCommandGroup)
async def image_group(ctx: lb.Context) -> None:
    """Apply modifications to an image

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
    """


# @image_group.child()
# @lb.option("effect", "effect to apply", choices=["Blur", "Warp"])
# @lb.option(
#     "image",
#     "image to modify",
#     hk.Attachment,
# )
# @lb.command("from-attachment", "Upload locally stored images for processing")
# @lb.implements(lb.SlashSubCommand)
# async def from_attachment(ctx: lb.Context, image: hk.Attachment, effect: str) -> None:
#     """A function that applies a filter from the given ones to an image and returns it

#     Args:
#         ctx (lb.Context): The message context
#         image (hk.Attachment): The image attachment
#         effect (Sequence[str]): The effect that is to be applied on the input image
#     """


@image_group.child()
@lb.option(
    "effect",
    "effect to apply",
    choices=["Blurple", "Remove Background", "Color Palette", "Posterize"],
)
@lb.option("image", "Image to modify (defaults to your pfp)", str, required=False)
@lb.command(
    "from-link", "Use an image from the internet for processing", pass_options=True
)
@lb.implements(lb.SlashSubCommand)
async def from_link(ctx: lb.Context, image: Optional[str], effect: str) -> None:
    """A function that applies a filter from the given ones to an image and returns it

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        image (str): The image link. Defaults to the user's pfp
        effect (str): The effect that is to be applied on the input image
    """

    if not image:
        image = ctx.author.avatar_url.url

    await ctx.respond(
        hk.Embed(
            description="Image Received, now processing...", color=0x00FFFF
        ).set_image("https://i.imgur.com/GinlBL8.gif")
    )

    if not is_image(image):
        wfu = random.choice(("Marin", "Shinobu", "Megumin"))
        if wfu == "Marin":
            waifu_pic = (
                await (
                    await ctx.bot.d.aio_session.get(
                        "https://api.waifu.im/search/?included_tags=marin-kitagawa"
                    )
                ).json()
            )["images"][0]["url"]
        else:
            waifu_pic = (
                await (
                    await ctx.bot.d.aio_session.get(
                        f"https://api.waifu.pics/sfw/{wfu.lower()}"
                    )
                ).json()
            )["url"]
        await ctx.edit_last_response(
            hk.Embed(
                title="Nah, this ain't it ❌",
                description=f"That doesn't look like an image. \nFor now enjoy this cute {wfu} pic",
                color=0x00FFFF,
            ).set_image(waifu_pic),
            attachments=[],
        )
        return

    if effect == "Blurple":
        async with ctx.bot.d.aio_session.get(
            "https://some-random-api.ml/canvas/blurple", params={"avatar": image}
        ) as res:
            if res.ok:
                Image.open(io.BytesIO(await res.read())).convert("RGB").save(
                    f"pictures/{ctx.author.username}_blurple.jpg"
                )
                await ctx.edit_last_response(
                    hk.Embed(color=0x00FFFF).set_image(
                        f"pictures/{ctx.author.username}_blurple.jpg"
                    ),
                    attachments=[],
                )
            else:
                await ctx.respond(
                    "The process failed to fetch a response 😕",
                    flags=hk.MessageFlag.EPHEMERAL,
                )

    elif effect == "Remove Background":
        async with ctx.bot.d.aio_session.post(
            "https://api.remove.bg/v1.0/removebg",
            data={"image_url": image, "size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_KEY},
        ) as res:
            if res.ok:
                Image.open(io.BytesIO(await res.read())).save(
                    f"pictures/{ctx.author.username}_nobg.png"
                )
                await ctx.edit_last_response(
                    hk.Embed(color=0x00FFFF).set_image(
                        f"pictures/{ctx.author.username}_nobg.png"
                    ),
                    attachments=[],
                )
            else:
                await ctx.respond(
                    "The process failed to fetch a response 😕",
                    flags=hk.MessageFlag.EPHEMERAL,
                )

    elif effect == "Color Palette":
        image = io.BytesIO(await (await ctx.bot.d.aio_session.get(image)).read())
        img = await color_palette(
            fast_colorthief.get_dominant_color(image, 1),
            fast_colorthief.get_palette(image, color_count=5, quality=1),
        )
        img = img.convert("RGB")
        image = Image.open(image).convert("RGB")  # .resize((300, 300))
        # img.paste(Image.new("RGB", (310,310), color=0x00FFFF).putalpha(175), (80,181,390,491))
        image = ImageOps.contain(image, (300, 300))
        image = ImageOps.expand(image, border=5, fill=(0, 255, 255))
        x_len, y_len = image.size
        img.paste(image, (82, 183, 82 + x_len, 183 + y_len))
        num = random.randint(1, 400)
        img.save(f"pictures/visual/{num}.png")
        await ctx.edit_last_response(
            hk.Embed(color=0x00FFFF).set_image(f"pictures/visual/{num}.png"),
            attachments=[],
        )
    elif effect == "Posterize":
        async with ctx.bot.d.aio_session.get(image) as resp:
            image = io.BytesIO(await resp.read())
            # image = io.BytesIO((await (await ctx.bot.d.aio_session.get(image)).read()))
            image = Image.open(image).convert("RGB")
            image = ImageOps.posterize(image, 3)
            num = random.randint(1, 400)
            image.save(f"pictures/visual/{num}_poster.png")
            await ctx.edit_last_response(
                hk.Embed(color=0x00FFFF).set_image(f"pictures/visual/{num}_poster.png"),
                attachments=[],
            )


async def color_visualize(
    hex_code: str, info_text: str = None, html_color: str = None
) -> Image.Image:
    """The function to apply the template of the colour visualize effect

    Args:
        hex_code (str): The hex code of the query colour
        info_text (str, optional): The text which contains info about the colour, defaults to None.
        html_color (str, optional): Closest HTML5 colour to the given colour, defaults to None.

    Returns:
        Image.Image: The cool pillow object with the template and stuff
    """

    img_font = ImageFont.truetype("resources/fonts/TTNorms-Medium.otf", size=30)

    mask = Image.new("RGBA", (960, 722), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.polygon([(0, 0), (0, 722), (357, 722), (117, 0)], fill=hex_code)
    draw.text((440, 270), info_text, fill=(255, 255, 255), font=img_font)
    draw.text((480, 640), html_color, fill=(255, 255, 255), font=img_font)

    img = Image.open(
        f"resources/visualize/{random.choice(os.listdir('resources/visualize'))}"
    ).convert("RGBA")

    return Image.composite(mask, img, mask)


@image_plugin.command
@lb.option(
    "color",
    "The color to visualize",
    hk.Color,
)
@lb.command(
    "visualize",
    "Show the visualization of a colour and its details",
    aliases=["cv", "colorinfo"],
    pass_options=True,
    auto_defer=True,
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def visualize(ctx: lb.Context, color: hk.Color) -> None:
    """Visualize a colour and get some info related to it

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        color (hk.Color): The colour of the image (hex, RGB etc.)
    """

    if isinstance(ctx, lb.SlashContext):
        color = hk.Color.of(color)
    if f"{color.hex_code}.png" in os.listdir("pictures/visual/"):
        await ctx.respond(attachment=f"pictures/visual/{color.hex_code}.png")
        return

    # TD remove the typing for slash command
    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        async with ctx.bot.d.aio_session.get(
            "https://www.thecolorapi.com/id", params={"hex": color.raw_hex_code}
        ) as resp:
            if resp.ok:
                resp = await resp.json()
                # print(resp)
                text1 = f"\nHex Code: {color.hex_code} \n\n \
                RGB Value: {color.rgb} \n\nHTML5 Color: {resp['name']['exact_match_name']}"
                text2 = f"{resp['name']['closest_named_hex']} ({resp['name']['value']})"

        img = await color_visualize(color.hex_code, text1, text2)
        img.save(f"pictures/visual/{color.hex_code}.png")
        await ctx.respond(attachment=f"pictures/visual/{color.hex_code}.png")


@image_plugin.command
@lb.option(
    "image", "The image whose palette is to be generated", hk.Attachment, required=False
)
@lb.command(
    "palette", "Get the colour palette of an image", aliases=["cp"], pass_options=True
)
@lb.implements(lb.PrefixCommand)
async def palette(ctx: lb.Context, image: hk.Attachment = None) -> None:
    """Generate colour palette of the dominant colours of a given image

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        image (hk.Attachment, optional): The image whose palette is to be generated,
        defaults to user's pfp
    """

    if not image:
        image = ctx.author.avatar_url

    image = io.BytesIO(await image.read())

    # if num == 1:
    #     await ctx.respond(fast_colorthief.get_dominant_color(image, 1))
    # else:
    #     pass

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        img = await color_palette(
            fast_colorthief.get_dominant_color(image, 1),
            fast_colorthief.get_palette(image, color_count=5, quality=1),
        )
        img = img.convert("RGB")
        image = Image.open(image).convert("RGB")  # .resize((300, 300))
        # img.paste(Image.new("RGB", (310,310), color=0x00FFFF).putalpha(175), (80,181,390,491))
        image = ImageOps.contain(image, (300, 300))
        image = ImageOps.expand(image, border=5, fill=(0, 255, 255))
        x_len, y_len = image.size
        img.paste(image, (82, 183, 82 + x_len, 183 + y_len))
        num = random.randint(1, 999)
        img.save(f"pictures/visual/{num}.png")
        await ctx.respond(attachment=f"pictures/visual/{num}.png")


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(image_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(image_plugin)
