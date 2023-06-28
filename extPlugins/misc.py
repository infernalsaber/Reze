import io
from typing import Literal, Union, Optional
import requests
from PIL import Image
from bs4 import BeautifulSoup


import hikari as hk
from miru.ext import nav
import miru


async def get_top_colour(user: hk.Member) -> hk.Color:
    roles = (await user.fetch_roles())[1:]  # All but @everyone
    roles = sorted(
        roles, key=lambda role: role.position, reverse=True
    )  # sort them by position, then reverse the order to go from top role down
    top_color = "#000000"
    for role in (await user.fetch_roles())[::-1]:
        if role.color != hk.Color(0x000000):
            top_color = role.color

    return top_color


def get_dominant_colour(pillow_img: Image.Image, show: Optional[bool] = 0) -> hk.Color:
    pillow_img = pillow_img.resize((1, 1), resample=0)
    dominant_color: tuple = pillow_img.getpixel((0, 0))
    if show:
        pillow_img.resize((75, 75)).show()  # show the image if desired

    return dominant_color


def get_image_dominant_colour(link: str) -> hk.Color:
    return hk.Color.of(
        get_dominant_colour(Image.open(requests.get(link, stream=True, timeout=10).raw))
    )


def is_image(link: str) -> bool:
    try:
        Image.open(io.BytesIO(requests.get(link, timeout=10).content))
        return True
    except Image.UnidentifiedImageError:
        return False
    except Exception as e:
        print(e)
        return False


# import enum
def type_of_response(link: str) -> Literal["image", "json", "html", "unknown"]:
    response = requests.get(link, timeout=10)
    try:
        Image.open(io.BytesIO(response.content))
        return "image"
    except Image.UnidentifiedImageError:
        ...
    try:
        response.json()
        return "json"
    except:
        ...
    try:
        BeautifulSoup(response.text, "lxml")
        return "html"
    except Exception as e:
        return "unknown"


# Custom Error Classes
class CustomError(Exception):
    """Parent class for all custom errors the bot may encounter"""

    pass


class requestsFailedError(CustomError):
    """
    Exception raised when the API the request is fetched from fails
    """


class injectionRiskError(CustomError):
    """
    Exception raised when the input may risk injection of code into the database
    """


class fileSizeError(CustomError):
    """
    Exception raised when trying to handle a file over the Discord upload
    size limit (25MB as of May 2023)
    """


# Navigator Buttons Miru
class CustomPrevButton(nav.NavButton):
    """A custom previous button class"""

    def __init__(
        self,
        *,
        style: Union[hk.ButtonStyle, int] = hk.ButtonStyle.SECONDARY,
        label: Optional[str] = None,
        custom_id: Optional[str] = None,
        emoji: Union[hk.Emoji, str, None] = hk.Emoji.parse(
            "<:pink_arrow_left:1059905106075725955>"
        ),
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style, label=label, custom_id=custom_id, emoji=emoji, row=row
        )

    async def callback(self, ctx: miru.ViewContext):
        if self.view.current_page == 0:
            self.view.current_page = len(self.view.pages) - 1
        else:
            self.view.current_page -= 1
        await self.view.send_page(ctx)

    async def before_page_change(self) -> None:
        ...


class CustomNextButton(nav.NavButton):
    """A custom next button class"""

    def __init__(
        self,
        *,
        style: Union[hk.ButtonStyle, int] = hk.ButtonStyle.SECONDARY,
        label: Optional[str] = None,
        custom_id: Optional[str] = None,
        emoji: Union[hk.Emoji, str, None] = hk.Emoji.parse(
            "<:pink_arrow_right:1059900771816189953>"
        ),
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style, label=label, custom_id=custom_id, emoji=emoji, row=row
        )

    async def callback(self, ctx: miru.ViewContext):
        if self.view.current_page == len(self.view.pages) - 1:
            self.view.current_page = 0
        else:
            self.view.current_page += 1
        await self.view.send_page(ctx)

    async def before_page_change(self) -> None:
        ...


# General Miru Buttons
class GenericButton(miru.Button):
    """A custom next general class"""

    # Let's leave our arguments dynamic this time, instead of hard-coding them
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ViewContext) -> None:
        # await ctx.respond("This is the only correct answer.", flags=hk.MessageFlag.EPHEMERAL)
        self.view.answer = self.label
        self.view.stop()


class KillButton(miru.Button):
    """A custom next kill class"""

    # Let's leave our arguments dynamic this time, instead of hard-coding them
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ViewContext) -> None:
        # await ctx.respond("This is the only correct answer.", flags=hk.MessageFlag.EPHEMERAL)
        await ctx.bot.rest.edit_message(
            ctx.channel_id, ctx.message, flags=hk.MessageFlag.SUPPRESS_EMBEDS
        )
        self.view.stop()
