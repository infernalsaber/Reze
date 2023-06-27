from datetime import datetime
from typing import Optional

import hikari as hk
import lightbulb as lb

util_plugin = lb.Plugin("Utility", "Commands intended to up the UX")

"""
#TODO
1. Implement a /embed command with option to add which channel to send to ✅
2. Implement a /announce command (options for role mention and channel) ✔
"""


@util_plugin.command
@lb.option(
    "image",
    "The image in question",
    str,
)
@lb.option("tag", "The ???", str)
@lb.option("name", "The name of the sticker", str)
@lb.command("makesticker", "Make a sticker", pass_options=True)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def sticker_upload(ctx: lb.Context, name: str, tag: str, image: str) -> None:
    await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    await util_plugin.bot.rest.create_sticker(ctx.get_guild(), name, tag, hk.URL(image))
    await ctx.respond("Uploaded sticker")


@util_plugin.command
@lb.option(
    "emoji",
    "The emoji to remove",
    hk.Emoji,
)
@lb.command("rememoji", "Remove an emoji", pass_options=True)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def sticker_upload(ctx: lb.Context, emoji: hk.Emoji) -> None:
    # await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    print(emoji)
    await util_plugin.bot.rest.delete_emoji(ctx.get_guild(), emoji)
    await ctx.respond("Deleted emoji.")


@util_plugin.command
@lb.option("thumbnail", "The url of the thumbnail, if any", str, required=False)
@lb.option("link", "The redirect url of the title", str, required=False)
@lb.option("footer", "Add a requested by: footer?", bool, required=False)
@lb.option("image", "The url of the image, if any", str, required=False)
@lb.option("title", "The title of the embed", str, required=False)
@lb.option(
    "content",
    "The content of the embed",
    str,
)
@lb.command("embed", "Make an embed message", pass_options=True)
@lb.implements(lb.SlashCommand)
async def make_embed(
    ctx: lb.Context,
    content: str,
    title: str = None,
    image: str = None,
    footer: bool = False,
    link: str = None,
    thumbnail: str = None,
) -> None:
    embed = (
        hk.Embed(description=content, title=title, url=link)
        .set_image(image)
        .set_thumbnail(thumbnail)
    )

    if footer:
        embed.set_footer(f"Requested by: {ctx.author}", icon=ctx.author.avatar_url)

    await ctx.respond(embed)


@util_plugin.command
@lb.option("image", "The url of an image, if to embed", str, required=False)
@lb.option("role2", "If one wasn't enough", hk.Role, required=False)
@lb.option("footer", "Add a from footer?", bool, required=False)
@lb.option(
    "role", "The role to ping with the announcement, if any", hk.Role, required=False
)
@lb.option(
    "content",
    "The content of the announcement",
    str,
)
@lb.option(
    "channel",
    "The channel to send the message in",
    hk.TextableGuildChannel,
)
@lb.command("announce", "Make an announcement", pass_options=True)
@lb.implements(lb.SlashCommand)
async def make_embed(
    ctx: lb.Context,
    channel: hk.TextableGuildChannel,
    content: str,
    role: hk.Role = None,
    footer: bool = False,
    role2: hk.Role = hk.undefined.UNDEFINED,
    image: str = None,
) -> None:
    roles = []
    if role:
        roles.append(role.mention)
    if role2:
        roles.append(role2.mention)
    roles = " ".join(roles) if not roles == [] else ""
    await util_plugin.bot.rest.create_message(
        channel=channel,
        embed=hk.Embed().set_image(image) if image else hk.undefined.UNDEFINED,
        content=f"{roles}\n\n {content}",
        role_mentions=True,
        mentions_everyone=True,
    )
    await ctx.respond("👌")


@util_plugin.command
@lb.option("text", "The text to repeat", str, modifier=lb.OptionModifier.CONSUME_REST)
@lb.command("echo", "Repeat")
@lb.implements(lb.PrefixCommand)
async def make_embed(ctx: lb.Context) -> None:
    await ctx.respond(
        ctx.options.text, user_mentions=True, role_mentions=True, mentions_everyone=True
    )


@util_plugin.command
@lb.add_checks(lb.owner_only)
@lb.option("code", "The plugin content", str, modifier=lb.OptionModifier.CONSUME_REST)
@lb.command("addplugin", "Add a plugin", aliases=["ap"], pass_options=True)
@lb.implements(lb.PrefixCommand)
async def make_embed(ctx: lb.Context, code: str) -> None:
    with open("extensions/new.py", "a+") as f:
        f.write(code)
    ctx.bot.load_extensions("extensions.new")
    await ctx.respond("Done👍", delete_after=5)


@util_plugin.command
@lb.add_checks(lb.owner_only)
@lb.command("backup", "Take a backup of the db")
@lb.implements(lb.PrefixCommand)
async def make_embed(ctx: lb.Context) -> None:
    await ctx.respond(attachment="botdb.db")


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(util_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(util_plugin)
