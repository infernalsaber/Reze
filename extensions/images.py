from typing import Optional, Union, Sequence
import datetime
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageFilter
import io
import os
import fast_colorthief

import hikari as hk
import lightbulb as lb

from extPlugins.misc import is_image

import dotenv
dotenv.load_dotenv()

REMOVE_BG_KEY = os.environ["removeBG_key"]

import random

image_plugin = lb.Plugin("Image Tools", "Apply cool and useful effects to images")

"""

#TODO


1. Generate palette from the given image (implement it like a card)
2. Filters: Blurple, Sharpen etc. + Color Visualize 
3. Masked Wordcloud
4. Remove BG
5. Compress Image
6. Background Blur
7. Colourize(?)
"""

async def color_palette(dominantColor: tuple, paletteColors: Sequence[tuple]) -> Image.Image:
    imgFont = ImageFont.truetype("resources/fonts/TTNorms-Light.otf", size=30)
    mask = Image.new("RGBA", (960,722), (0,0,0,0))
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(45, 595), (430, 645)], 30, dominantColor)
    draw.text((175, 604), str(hk.Color.of(dominantColor).hex_code), fill=(255,255,255), font=imgFont)

    # ![pillow_composite_circle](data/dst/pillow_composite_circle.jpg)
    # mask.show()

    img = Image.open(f"resources/palette/{random.choice(os.listdir('resources/palette'))}").convert("RGBA")
    # img.show()
    final = Image.composite(mask, img, mask)
    # imgFont = ImageFont.load_default()

    # final.show()
    
    for i, color in enumerate(paletteColors):
        color = hk.Color.of(color).hex_code
        mask = Image.new("RGBA", (960,722), (0,0,0,0))
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(496, 271+(66*i)), (884, 322+(66*i))], 30, color)
        draw.text((625, 280+(66*i)), f"{color}", fill=(255,255,255), font=imgFont)
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
async def image_group(
    ctx: lb.Context
) -> None:
    pass




@image_group.child()
@lb.option("effect", "effect to apply", choices=["Blur", "Warp"])
@lb.option("image", "image to modify", hk.Attachment, )
@lb.command("from-attachment", "Upload locally stored images for processing")
@lb.implements(lb.SlashSubCommand)
async def from_attachment(
    ctx: lb.Context, image: hk.Attachment, effect: str
    ) -> None:
    """A function that applies a filter from the given ones to an image and returns it

    Args:
        ctx (lb.Context): The message context
        image (hk.Attachment): The image attachment
        effect (Sequence[str]): The effect that is to be applied on the input image
    """


@image_group.child()
@lb.option("effect", "effect to apply", choices=["Blurple", "Remove Background", "Color Palette", "Posterize"])
@lb.option("image", "Image to modify (defaults to your pfp)", str, required=False)
@lb.command("from-link", "Use an image from the internet for processing", pass_options=True)
@lb.implements(lb.SlashSubCommand)
async def from_link(
    ctx: lb.Context, image: Optional[str], effect: str
    ) -> None:
    if not image:
        image = ctx.author.avatar_url.url
    
    await ctx.respond(
        hk.Embed(
            description=f"Image Received, now processing...", 
            color=0x00FFFF
        )
        .set_image("https://mir-s3-cdn-cf.behance.net/project_modules/max_632/04de2e31234507.564a1d23645bf.gif")
    )

    if not is_image(image):
        wf = random.choice(("Marin", "Shinobu", "Megumin"))
        if wf == "Marin":
            waifu_pic = (await (await ctx.bot.d.aio_session.get(f"https://api.waifu.im/search/?included_tags=marin-kitagawa")).json())['images'][0]['url']
        else:
            waifu_pic = (await (await ctx.bot.d.aio_session.get(f"https://api.waifu.pics/sfw/{wf.lower()}")).json())['url']
        await ctx.edit_last_response(
            hk.Embed(
                title="Nah, this ain't it ❌",
                description=f"That doesn't look like an image. \nFor now enjoy this cute {wf} pic",
                color=0x00FFFF
            )
            .set_image(waifu_pic)
            , attachments=[]
        )
        return

    if effect == "Blurple":
        async with ctx.bot.d.aio_session.get(
        "https://some-random-api.ml/canvas/blurple", params=dict(avatar=image)
        ) as res:
            if res.ok:
                Image.open(io.BytesIO(await res.read())).convert("RGB").save(f"pictures/{ctx.author.username}_blurple.jpg")
                await ctx.edit_last_response(
                    hk.Embed(color=0x00FFFF)
                    .set_image(f"pictures/{ctx.author.username}_blurple.jpg")
                    , attachments=[]
                )
            else:
                await ctx.respond("The process failed to fetch a response 😕", flags=hk.MessageFlag.EPHEMERAL)

    elif effect == "Remove Background":
        async with ctx.bot.d.aio_session.post(
        "https://api.remove.bg/v1.0/removebg",
        data=dict(image_url=image, size="auto"),
        headers={'X-Api-Key': REMOVE_BG_KEY}
        ) as res:
            if res.ok:
                Image.open(io.BytesIO(await res.read())).save(f"pictures/{ctx.author.username}_nobg.png")
                await ctx.edit_last_response(
                    hk.Embed(color=0x00FFFF)
                    .set_image(f"pictures/{ctx.author.username}_nobg.png")
                    , attachments=[]
                )
            else:
                await ctx.respond("The process failed to fetch a response 😕", flags=hk.MessageFlag.EPHEMERAL)

    elif effect == "Color Palette":
        image = io.BytesIO(await (await ctx.bot.d.aio_session.get(image)).read())
        img = await color_palette(fast_colorthief.get_dominant_color(image, 1), fast_colorthief.get_palette(image, color_count=5, quality=1))
        img = img.convert("RGB")
        image = Image.open(image).convert("RGB") #.resize((300, 300))
        # img.paste(Image.new("RGB", (310,310), color=0x00FFFF).putalpha(175), (80,181,390,491))
        image = ImageOps.contain(image, (300, 300))
        image = ImageOps.expand(image, border=5, fill=(0,255,255))
        x,y = image.size
        img.paste(image, (82, 183, 82+x, 183+y))
        num = random.randint(1, 400)
        img.save(f"pictures/visual/{num}.png")
        await ctx.edit_last_response(
            hk.Embed(color=0x00FFFF)
            .set_image(f"pictures/visual/{num}.png")
            , attachments=[]
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
                hk.Embed(color=0x00FFFF)
                .set_image(f"pictures/visual/{num}_poster.png")
                , attachments=[]
            )


async def color_visualize(hexCode: str, infoText: str=None, htmlColor:str=None) -> Image.Image:
    
    imgFont = ImageFont.truetype("resources/fonts/TTNorms-Medium.otf", size=30)

    mask = Image.new("RGBA", (960,722), (0,0,0,0))
    draw = ImageDraw.Draw(mask)
    draw.polygon([(0,0), (0,722), (357, 722), (117, 0)], fill=hexCode)
    draw.text((440, 270), infoText, fill=(255,255,255), font=imgFont)
    draw.text((480, 640), htmlColor, fill=(255,255,255), font=imgFont)


    img = Image.open(f"resources/visualize/{random.choice(os.listdir('resources/visualize'))}").convert("RGBA")
    return Image.composite(mask, img, mask)

@image_plugin.command
@lb.option(
    "color", "The color to visualize", hk.Color, 
)
@lb.command(
    "visualize", "Show the visualization of a colour and its details", aliases=["cv", "colorinfo"], pass_options=True
)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def visualize(ctx: lb.Context, color: hk.Color) -> None:    
    if isinstance(ctx, lb.SlashContext):
        await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    if f"{color.hex_code}.png" in os.listdir("pictures/visual/"):
        await ctx.respond(attachment=f"pictures/visual/{color.hex_code}.png")
        return

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        async with ctx.bot.d.aio_session.get(
            "https://www.thecolorapi.com/id", params=dict(hex=color.raw_hex_code)
        ) as resp:
            if resp.ok:
                resp = await resp.json()
                # print(resp)
                text1 = f"\nHex Code: {color.hex_code} \n\nRGB Value: {color.rgb} \n\nHTML5 Color: {resp['name']['exact_match_name']}"
                text2 = f"{resp['name']['closest_named_hex']} ({resp['name']['value']})"

        img = await color_visualize(color.hex_code, text1, text2) 
        img.save(f"pictures/visual/{color.hex_code}.png")
        await ctx.respond(attachment=f"pictures/visual/{color.hex_code}.png")
    
 

@image_plugin.command
@lb.option(
    "num", "The number of colors", int, required=False
)
@lb.option(
    "image", "The image whose palette is to be generated", hk.Attachment, required=False
)
@lb.command(
    "palette", "Get the colour palette of an image", aliases=["cp"], pass_options=True
)
@lb.implements(lb.PrefixCommand)
async def palette(ctx: lb.Context, image: hk.Attachment = None, num: int = None) -> None: 
    if not image:
        image = ctx.author.avatar_url

    image = io.BytesIO(await image.read())

    if num == 1:
        await ctx.respond(fast_colorthief.get_dominant_color(image, quality))
    else:
        pass

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        img = await color_palette(fast_colorthief.get_dominant_color(image, 1), fast_colorthief.get_palette(image, color_count=5, quality=1))
        img = img.convert("RGB")
        image = Image.open(image).convert("RGB") #.resize((300, 300))
        # img.paste(Image.new("RGB", (310,310), color=0x00FFFF).putalpha(175), (80,181,390,491))
        image = ImageOps.contain(image, (300, 300))
        image = ImageOps.expand(image, border=5, fill=(0,255,255))
        x,y = image.size
        img.paste(image, (82, 183, 82+x, 183+y))
        num = random.randint(1, 999)
        img.save(f"pictures/visual/{num}.png")
        await ctx.respond(attachment=f"pictures/visual/{num}.png")


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(image_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(image_plugin)