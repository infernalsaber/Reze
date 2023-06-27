import hikari as hk
import lightbulb as lb
import miru

from datetime import datetime
from typing import Optional
import psutil

from extPlugins.misc import get_top_colour, get_image_dominant_colour
from extensions.dir import GenericButton


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
@lb.command("userinfo", "Get info on a server member.", pass_options=True, aliases=["user"])
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
@lb.command("serverinfo", "Get general info about the server", aliases=["server"])
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

@info_plugin.command
@lb.command("botinfo", "Get general info about the server", aliases=["info"])
@lb.implements(lb.PrefixCommand)
async def userinfo(ctx: lb.Context) -> None:
    user = info_plugin.bot.get_me()
    data = await info_plugin.bot.rest.fetch_application()
    # print(data.owner)
    guilds = [e for e in await info_plugin.bot.rest.fetch_my_guilds()]
    # print(guilds)
    
    member = 0
    for guild in list(info_plugin.bot.cache.get_members_view()):
        guild_obj = info_plugin.bot.cache.get_guild(guild)
        member = member + guild_obj.member_count

    view = miru.View()
    view.add_item(
        GenericButton(
            style=hk.ButtonStyle.SECONDARY, 
            label="Changelog",
            emoji=hk.Emoji.parse("<:MIU_changelog:1108056158377349173>")
        )
    )

    response = await ctx.respond(
        hk.Embed(
            color=0x00FFFF,
            description="A multi-purpose discord bot \
                written in hikari-py."


        )
        .add_field("Name", user)
        .add_field("No of Servers", len(guilds), inline=True)
        .add_field("No of Members", member, inline=True)
        .add_field("Version", "v0.2.0")
        .add_field("Alive since", f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        .add_field("Up since", f"<t:{int(info_plugin.bot.d.timeup.timestamp())}:R>", inline=True)
        .add_field(
            "System Usage", 
            f"RAM: {psutil.virtual_memory()[2]}% (of 512MB) \nCPU: {psutil.cpu_percent(4)}%")
        # .add_field(
        #     "About", 
        #     "A multi-purpose discord bot written in hikari-py. \
        #         \nUse `-help` for help or `-help <cmd>` for \
        #             help about a command. ")
        .set_author(name=f"{user.username} Bot")
        .set_thumbnail(user.avatar_url)
        .set_image("https://media.discordapp.net/attachments/1005948828484108340/1108082051246198824/69886913365.png")
        .set_footer(
            f"Made by: {data.owner}", 
            icon=data.owner.avatar_url)
        , components = view
    )

    await view.start(response)
    await view.wait()
    if(hasattr(view, "answer")):
        async with ctx.bot.d.aio_session.get(
            "https://api.github.com/repos/infernalsaber/reze/commits"
        ) as response:
            if response.ok:
                response = await response.json()
                changes = ""
                for i in range(4):
                    changes += f'{i+1}. `{response[i]["commit"]["committer"]["date"]}`'
                    changes += ":\u1CBC\u1CBC"
                    changes += response[i]["commit"]["message"].split("\n")[0]
                    changes += "\n"

                await ctx.respond(
                    embed = hk.Embed(
                        description=changes,
                        color=0x00FFFF
                    ).set_author(name="Bot Changelog (Recent)"),
                    # reply = True,
                    flags = hk.MessageFlag.EPHEMERAL
                )
            else:
                await ctx.respond(
                    "Failed to get changelog info.",
                    reply = True,
                    flags = hk.MessageFlag.EPHEMERAL
                )
    # for guild in guilds:
    #     print(guild.member_count)
    # a = list(info_plugin.bot.cache.get_members_view())
    # print(info_plugin.bot.cache.get_members_view())
    # print(a)
    # print(len(a))
    
    # # print(list(info_plugin.bot.rest.fetch_my_guilds()))
    # member = 0

    # print(member)

@info_plugin.command
@lb.option(
    "role", "The role to get information about.", hk.Role
)
@lb.command("roleinfo", "Get info on a role", pass_options=True, aliases=["role"])
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def role_info(ctx: lb.Context, role: hk.Role) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return
        
    await ctx.respond(
        hk.Embed(
            title=f"Role: {role.name}",
            description=f"Role ID: `{role.id}`",
            colour=role.color,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.display_avatar_url,
        )
        .add_field(
            "Color",
            role.color.hex_code,
            inline=True,
        )
        .add_field(
            "Icon",
            f"(Link)[{role.icon_url}]",
            inline=True,
        )
        .add_field(
            "Created At",
            f"<t:{int(role.created_at.timestamp())}:R>",
            # inline=True,
        )
        .set_thumbnail(role.icon_url)
    )

@info_plugin.command
@lb.option(
    "emote", "The emote to get information about.", hk.Emoji
)
@lb.command("emoteinfo", "Get info on a role", pass_options=True, aliases=["emote, emoji"])
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def emoji_info(ctx: lb.Context, emoji: hk.Emoji) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    await ctx.respond(
        hk.Embed(
            title=f"Emoji: {emoji.name}",
            description=f"Idk wtf this is: `{emoji.mention}`",
            colour=get_image_dominant_colour(emoji.url) or 0xf4eae9,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.display_avatar_url,
        )
        .add_field(
            "Image",
            f"Link[{emoji.url}]",
            # inline=True,
        )
        .set_thumbnail(emoji.url)
    )


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(info_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(info_plugin)