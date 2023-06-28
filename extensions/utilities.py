"""Utility commands for the bot"""
import hikari as hk
import lightbulb as lb

util_plugin = lb.Plugin("Utility", "Commands intended to up the UX")


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
    """Make a sticker

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        name (str): Name of the sticker
        tag (str): Tage for the sticker
        image (str): Image for the sticker
    """

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
async def remove_emoji(ctx: lb.Context, emoji: hk.Emoji) -> None:
    """Remove an emoji

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        emoji (hk.Emoji): The emoji to remove
    """

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
    """Generate an embed message

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        content (str): The content of the embed
        title (str, optional): Title of the embed. Defaults to None.
        image (str, optional): Image to embed. Defaults to None.
        footer (bool, optional): Whether to add a footer. Defaults to False.
        link (str, optional): Link for the embed. Defaults to None.
        thumbnail (str, optional): Url for the thumbnail. Defaults to None.
    """
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
async def announce(
    ctx: lb.Context,
    channel: hk.TextableGuildChannel,
    content: str,
    role: hk.Role = None,
    # footer: bool = False,
    role2: hk.Role = hk.undefined.UNDEFINED,
    image: str = None,
) -> None:
    """Make an announcement using the bot

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        channel (hk.TextableGuildChannel): The channel to announce in
        content (str): The content of the message
        role (hk.Role, optional): Role 1 to ping. Defaults to None.
        role2 (hk.Role, optional): If one Role ping wasn't enough. Defaults to hk.UNDEFINED.
        image (str, optional): An image to embed (if any). Defaults to None.
    """

    roles = []
    if role:
        roles.append(role.mention)
    if role2:
        roles.append(role2.mention)
    roles = " ".join(roles) if not roles else ""
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
async def echo(ctx: lb.Context) -> None:
    """Repeat the argument text"""
    await ctx.respond(
        ctx.options.text, user_mentions=True, role_mentions=True, mentions_everyone=True
    )


@util_plugin.command
@lb.add_checks(lb.owner_only)
@lb.option("code", "The plugin content", str, modifier=lb.OptionModifier.CONSUME_REST)
@lb.command("addplugin", "Add a plugin", aliases=["ap"], pass_options=True)
@lb.implements(lb.PrefixCommand)
async def add_plugin(ctx: lb.Context, code: str) -> None:
    """Code directly from Discord (untested)"""

    with open("extensions/new.py", "a+", encoding="utf-8") as pyfile:
        pyfile.write(code)
    ctx.bot.load_extensions("extensions.new")
    await ctx.respond("Done👍", delete_after=5)


@util_plugin.command
@lb.add_checks(lb.owner_only)
@lb.command("backup", "Take a backup of the db")
@lb.implements(lb.PrefixCommand)
async def backup(ctx: lb.Context) -> None:
    """Send a backup of the DB"""
    await ctx.respond(attachment="botdb.db")


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(util_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(util_plugin)
