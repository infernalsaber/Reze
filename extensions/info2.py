from datetime import datetime
from typing import Optional

import hikari as hk
import lightbulb as lb

from extPlugins.misc import get_top_colour, get_image_dominant_colour

info_plugin = lb.Plugin("Info", "Get information about an entity")

"""
#TODO
1. Fix the layout ✅
2. Add user banner as image ✅
3. Server Info ✅
"""

@info_plugin.command
@lb.option(
    "user", "The user to get information about.", hk.User, required=False
)
@lb.command("userinfo", "Get info on a server member.", pass_options=True)
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def userinfo(ctx: lb.Context, user: Optional[hk.User] = None) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    user = user or ctx.author
    user = ctx.bot.cache.get_member(guild, user)

    if not user:
        await ctx.respond("That user is not in the server.")
        return


    embedColor = await get_top_colour(user)
    roles = (await user.fetch_roles())[1:]
        
    await ctx.respond(
        hk.Embed(
            title=f"User: {user.display_name}",
            description=f"User ID: `{user.id}`",
            colour=embedColor,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.display_avatar_url,
        )
        .add_field(
            "Bot?",
            "Yes" if user.is_bot else "No",
            inline=True,
        )
        .add_field(
            "Account Created",
            f"<t:{int(user.created_at.timestamp())}:R>",
            inline=True,
        )
        .add_field(
            "Server Joined",
            f"<t:{int(user.joined_at.timestamp())}:R>",
            inline=True,
        )
        .add_field(
            "Roles",
            ", ".join(r.mention for r in roles),
            inline=False,
        )
        .set_thumbnail(user.avatar_url)
        .set_image(user.banner_url)
    )
    # ctx.bot.rest.search_members(guild, name)
    # ctx.bot.update_presence()
    # ctx.bot.rest.create
    # await ctx.respond(user.avatar_url)
    # await ctx.respond(user.make_avatar_url())

@info_plugin.command
@lb.command("serverinfo", "Get general info about the server")
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def userinfo(ctx: lb.Context) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    guild = ctx.get_guild()
    guild_icon = guild.icon_url
    await ctx.respond(
        hk.Embed(
            color=get_image_dominant_colour(guild_icon) or 0xf4eae9, #the dominant colour of the image
            title=f"Server: {guild.name}",
            description=f"Server ID: `{guild.id}`",
            timestamp=datetime.now().astimezone()
        )
        .add_field("Owner", await guild.fetch_owner(), inline=True)
        .add_field("Server Created", f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        .add_field("Member Count", guild.member_count)
        .add_field("Boosts", guild.premium_subscription_count or "NA", inline=True)
        .add_field("Boost Level", guild.premium_tier or "NA", inline=True)
        .set_thumbnail(guild_icon)
        .set_image(guild.banner_url)
    )

def load(bot: lb.BotApp) -> None:
    bot.add_plugin(info_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(info_plugin)