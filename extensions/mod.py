"""Moderation commands for a guild"""
import datetime
from typing import Optional

import asyncio
import isodate

import hikari as hk
import lightbulb as lb
from hikari import Permissions


mod_plugin = lb.Plugin(
    "Moderation Commands", "Self explanatory. Cool and powerful moderation tools"
)


"""
#TODO
1. Use database for variables (sqlite?)✅
2. Implement mute command ✅
3. Implement hide channel command ~(in progress)
"""


@mod_plugin.command
@lb.add_cooldown(5, 1, lb.UserBucket)
@lb.add_cooldown(10, 2, lb.ChannelBucket)
@lb.add_checks(
    lb.has_channel_permissions(hk.Permissions.MANAGE_MESSAGES),
    lb.bot_has_channel_permissions(hk.Permissions.MANAGE_CHANNELS),
)
@lb.option("messages", "The number of messages to purge")
@lb.command("purge", "Purge messages", aliases=["clear"])
@lb.implements(lb.SlashCommand, lb.PrefixCommand)
async def purge(ctx: lb.Context) -> None:
    """Purge n messages"""
    if isinstance(ctx, lb.PrefixContext):
        await ctx.event.message.delete()

    msgs = await ctx.bot.rest.fetch_messages(ctx.channel_id).limit(
        int(ctx.options.messages)
    )
    await ctx.bot.rest.delete_messages(ctx.channel_id, msgs)

    await ctx.respond(f"{len(msgs)} messages deleted. ", delete_after=3)


@mod_plugin.command
@lb.add_checks(
    lb.has_guild_permissions(hk.Permissions.KICK_MEMBERS),
    lb.bot_has_guild_permissions(hk.Permissions.KICK_MEMBERS),
)
@lb.option(
    "reason",
    "The reason said user was kicked",
    str,
    required=False,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.option("user", "The user to kick", hk.guilds.Member)
@lb.command(
    "kick", "Kick a user in the ass", pass_options=True, aliases=["kys", "fuckoff"]
)
@lb.implements(
    lb.PrefixCommand,
)
async def kick_user(ctx: lb.Context, user: hk.User, reason: Optional[str]) -> None:
    """Kick a user from a server

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        user (hk.User): The user to kick
        reason (Optional[str]): The reason the user is being kicked
    """

    if isinstance(ctx, lb.SlashContext):
        await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    if reason:
        await user.kick(reason=reason)
    else:
        await user.kick()
    await ctx.respond(f"Kicked `{user}` for `{reason}`")
    if not user.is_bot:
        await user.send(f"You were kicked from `{ctx.get_guild()}` for `{reason}`")


@mod_plugin.command
@lb.add_checks(
    lb.has_guild_permissions(hk.Permissions.MUTE_MEMBERS),
    lb.bot_has_guild_permissions(hk.Permissions.MUTE_MEMBERS),
)
@lb.option(
    "reason",
    "The reason said user was muted",
    str,
    required=False,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.option("time", "The timeout time", str)
@lb.option("user", "The user to mute", hk.guilds.Member)
@lb.command("mute", "Mute a user", pass_options=True, aliases=["stfu"])
@lb.implements(
    lb.PrefixCommand,
)
async def mute_user(
    ctx: lb.Context, user: hk.guilds.Member, time: str, reason: Optional[str]
) -> None:
    """Mute a user

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        user (hk.guilds.Member): The user to mute
        time (str): The time duration to mute for (eg. 2h, 1m etc.)
        reason (Optional[str]): The reason the user is muted
    """

    duration = datetime.datetime.now().astimezone() + isodate.parse_duration(
        f"PT{time.upper()}"
    )
    if isinstance(ctx, lb.SlashContext):
        await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    if reason:
        await user.edit(communication_disabled_until=duration, reason=reason)
    else:
        await user.edit(communication_disabled_until=duration)
    await ctx.respond(f"Muted `{user}` for `{time}` due to `{reason}`")
    if not user.is_bot:
        await user.send(f"You were muted in `{ctx.get_guild()}` for `{reason}`")
        isodate.parse_duration(f"PT{time.upper()}").total_seconds()
        await asyncio.sleep(isodate.parse_duration(f"PT{time.upper()}").total_seconds())
        await user.send(f"Mute in `{ctx.get_guild()}` expired")


# @mod_plugin.command
# @lb.add_checks(lb.has_guild_permissions(hk.Permissions.MUTE_MEMBERS))
# @lb.option(
#     "reason",
#     "The reason said user was muted",
#     str,
#     required=False,
#     modifier=lb.commands.OptionModifier.CONSUME_REST,
# )
# @lb.option("time", "The time to hard-mute for", str)
# @lb.option("user", "The user to mute", hk.guilds.Member)
# @lb.command("hardmute", "Hard mute a user", pass_options=True)
# @lb.implements(lb.PrefixCommand)
# async def hard_mute_user(
#     ctx: lb.Context, user: hk.guilds.Member, time: str, reason: Optional[str]
# ) -> None:
#     await ctx.respond("Sorry, command in development 👨‍🔬")


@mod_plugin.command
@lb.add_checks(
    lb.has_guild_permissions(hk.Permissions.BAN_MEMBERS),
    lb.bot_has_guild_permissions(hk.Permissions.BAN_MEMBERS),
)
@lb.option(
    "reason",
    "The reason said user was banned",
    str,
    required=False,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.option("user", "The user to ban", hk.guilds.Member)
@lb.command("ban", "Pull the 🔨", pass_options=True)
@lb.implements(
    lb.PrefixCommand,
)
async def ban_user(
    ctx: lb.Context, user: hk.guilds.Member, reason: Optional[str]
) -> None:
    """Ban a user

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        user (hk.guilds.Member): The user to ban
        reason (Optional[str]): The reason the user is being banned
    """

    if isinstance(ctx, lb.SlashContext):
        await ctx.respond(hk.ResponseType.DEFERRED_MESSAGE_CREATE)
    if reason:
        await user.ban(delete_message_days=1, reason=reason)
        # The delete_message_days -> delete_message_seconds in dev114
    else:
        await user.ban(delete_message_days=1)
    await ctx.respond(f"Banned `{user}` for `{reason}`")
    if not user.is_bot:
        await user.send(f"You were banned from `{ctx.get_guild()}` for `{reason}`")


@mod_plugin.command
@lb.add_checks(
    lb.has_guild_permissions(hk.Permissions.BAN_MEMBERS),
    lb.bot_has_guild_permissions(hk.Permissions.MODERATE_MEMBERS),
)
@lb.option(
    "reason",
    "The reason said user was unbanned",
    str,
    required=False,
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.option("user", "The user to unban", str)
@lb.command("unban", "Remove the 🔨", pass_options=True)
@lb.implements(
    lb.PrefixCommand,
)
async def unban_user(
    ctx: lb.Context, user: hk.Snowflake, reason: Optional[str]
) -> None:
    """Unban a user

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        user (hk.Snowflake): The user to unban (enter the user id)
        reason (Optional[str]): The reason for ban removal
    """

    if reason:
        await ctx.bot.rest.unban_member(ctx.guild_id, user, reason=reason)
    else:
        await ctx.bot.rest.unban_member(ctx.guild_id, user)
    await ctx.respond(f"Unbanned `{user}` for `{reason}`")


@mod_plugin.command
@lb.command("hide", "Hide👻 the channel")
@lb.implements(
    lb.PrefixCommand,
)
async def hide_channel(ctx: lb.Context) -> None:
    """Hide the current channel from the public"""

    overwrite = hk.PermissionOverwrite(
        id=980479965726404670,  # everyone role
        type=hk.PermissionOverwriteType.ROLE,
        allow=(Permissions.NONE),
        deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
    )
    # hk.PermissionOverwrite
    await mod_plugin.bot.rest.edit_channel(
        ctx.get_channel(), permission_overwrites=[overwrite]
    )
    await ctx.respond(
        f"Channel hidden {hk.Emoji.parse('<a:peacedisappear: 1061571520457080882>')}."
    )


@mod_plugin.command
@lb.command("unhide", "Show the channel", aliases=["show"])
@lb.implements(
    lb.PrefixCommand,
)
async def unhide_channel(ctx: lb.Context) -> None:
    """Unhide current channel from public"""

    overwrite = hk.PermissionOverwrite(
        id=980479965726404670,  # everyone role
        type=hk.PermissionOverwriteType.ROLE,
        allow=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
        deny=(Permissions.NONE),
    )
    # hk.PermissionOverwrite
    await mod_plugin.bot.rest.edit_channel(
        ctx.get_channel(), permission_overwrites=[overwrite]
    )
    await ctx.respond(
        f"Channel hidden no more {hk.Emoji.parse('<a:reappear: 1061572025782648893>')}."
    )


# @mod_plugin.command
# @lb.option("entity", "The user or role to hide channel from")
# @lb.command(
#     "hidefrom", "Hide👻 the channel from a user/role", pass_options=True, aliases=["hf"]
# )
# @lb.implements(lb.PrefixCommand)
# async def hide_from(ctx: lb.Context, entity: Union[hk.Member, hk.Role]) -> None:
#     await ctx.respond("Sorry, command in development 👨‍🔬")
#     return

# if isinstance(entity, hk.Member):
#     print("\n\nMember\n\n")
# if isinstance(entity, hk.User):
#     print("\n\nUser\n\n")
# if isinstance(entity, hk.Role):
#     print("\n\nRole\n\n")
# print("Might be none too lol. ")
# return
# # print(type(entity))
# # hk.Role
# # hk.Role.id
# if hk.User(entity).id:
#     print("Passes as user")
#     # print(entity.id)
# elif isinstance(entity, hk.Role):
#     print("Passes as role")
# else:
#     print("Passes as neither")

# overwrite = hk.PermissionOverwrite(
#     id=entity.id,
#     type=hk.PermissionOverwriteType.MEMBER,
#     allow=(Permissions.NONE),
#     deny=(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES),
# )
# # hk.PermissionOverwrite
# await mod_plugin.bot.rest.edit_channel(
#     ctx.get_channel(), permission_overwrites=[overwrite]
# )
# await ctx.respond(
#     f"Channel hidden {hk.Emoji.parse('<a:peacedisappear: 1061571520457080882>')}."
# )


@mod_plugin.command
@lb.command("Remove embed", "Remove an embed from a message")
@lb.implements(lb.MessageCommand)
async def remove_embed(ctx: lb.MessageContext):
    """Delete an embed from a message"""

    await ctx.respond(
        f"Deleting embed {hk.Emoji.parse('<a:loading_:1061933696648740945>')}"
    )
    await mod_plugin.bot.rest.edit_message(
        ctx.channel_id, ctx.options["target"], flags=hk.MessageFlag.SUPPRESS_EMBEDS
    )
    await ctx.edit_last_response("Deleted embed")
    asyncio.sleep(2)
    await ctx.delete_last_response()


@mod_plugin.command
@lb.command("lock", "Lock🔒 the channel")
@lb.implements(
    lb.PrefixCommand,
)
async def lock_channel(ctx: lb.Context) -> None:
    """Lock a channel from the public"""

    overwrite = hk.PermissionOverwrite(
        id=980479965726404670,
        type=hk.PermissionOverwriteType.ROLE,
        allow=(Permissions.VIEW_CHANNEL | Permissions.READ_MESSAGE_HISTORY),
        deny=(Permissions.MANAGE_MESSAGES | Permissions.SEND_MESSAGES),
    )
    # hk.PermissionOverwrite
    await mod_plugin.bot.rest.edit_channel(
        ctx.get_channel(), permission_overwrites=[overwrite]
    )
    await ctx.respond("Channel locked🔐.")


# await mod_plugin.bot.rest.edit


@mod_plugin.command
@lb.command("unlock", "Unlock🔓 the channel")
@lb.implements(
    lb.PrefixCommand,
)
async def unlock_channel(ctx: lb.Context) -> None:
    """Unlock a channel and let everyone use it"""

    overwrite = hk.PermissionOverwrite(
        id=980479965726404670,
        type=hk.PermissionOverwriteType.ROLE,
        allow=(
            Permissions.VIEW_CHANNEL
            | Permissions.READ_MESSAGE_HISTORY
            | Permissions.SEND_MESSAGES
        ),
        deny=(Permissions.MANAGE_MESSAGES),
    )
    # hk.PermissionOverwrite
    await mod_plugin.bot.rest.edit_channel(
        ctx.get_channel(), permission_overwrites=[overwrite]
    )
    await ctx.respond("Channel unlocked🔓.")


@mod_plugin.command
@lb.command("lockserv", "Lock the server⚡")
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def lock_server(ctx: lb.Context) -> None:
    """Lock down the entire server like in a raid"""
    # allowed_perms = Permissions.VIEW_CHANNEL | Permissions.CHANGE_NICKNAME |
    # Permissions.READ_MESSAGE_HISTORY | Permissions.ADD_REACTIONS
    await ctx.respond()
    overwrite = hk.PermissionOverwrite(
        id=980479965726404670,
        type=hk.PermissionOverwriteType.ROLE,
        allow=(Permissions.NONE),
        deny=(Permissions.MANAGE_MESSAGES | Permissions.SEND_MESSAGES),
    )
    # default perms = Permissions.
    async for channel in await mod_plugin.bot.rest.fetch_guild_channels(ctx.guild_id):
        await mod_plugin.bot.rest.edit_channel(
            channel, permission_overwrites=[overwrite]
        )

    # await mod_plugin.bot.rest.edit_role(
    # ctx.get_guild(), 980479965726404670, permissions=allowed_perms)
    await ctx.edit_last_response(
        f"Server has been locked {hk.Emoji.parse('<a:Lock:1061237840358408192>')}"
    )


@mod_plugin.command
@lb.command("unlockserv", "Unlock the server👐")
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def unlock_server(ctx: lb.Context) -> None:
    """Unlock the server to allow chatting again"""

    allowed_perms = (
        Permissions.VIEW_CHANNEL
        | Permissions.CHANGE_NICKNAME
        | Permissions.READ_MESSAGE_HISTORY
        | Permissions.ADD_REACTIONS
        | Permissions.SEND_MESSAGES
    )
    # Permissions(0x00)
    # default perms = Permissions.
    await mod_plugin.bot.rest.edit_role(
        ctx.get_guild(), 980479965726404670, permissions=allowed_perms
    )
    await ctx.respond(
        f"Server has been unlocked {hk.Emoji.parse('<a:unlock1:1061237870091833395>')}"
    )
    # ctx._maybe_defer()


@mod_plugin.command
@lb.option("userid", "The userid of the user to pre-ban")
@lb.command("preban", "Preban a user", pass_options=True)
@lb.implements(lb.PrefixCommand)
async def preban_create(ctx: lb.Context, userid: hk.Snowflake):
    """Preban a user who is percieved to be dangerous.
    They'd be banned upon joining the guild instantly

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        userid (hk.Snowflake): The user id to preban
    """

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        botdb = mod_plugin.bot.d.dbcon
        cur = botdb.cursor()

        cur.execute("INSERT INTO prebannedusers VALUES (?) ", (userid,))
        botdb.commit()
        await ctx.respond(f"Added user `<@{userid}>` to the preban list")


@mod_plugin.command
@lb.command("censor", "Censor a word", pass_options=True)
@lb.implements(lb.PrefixCommandGroup)
async def censor(ctx: lb.Context):
    """Censor a word (delete it upon being thrown in the server)"""


@censor.child
@lb.option("word", "The word to censor")
@lb.command(
    "add", "Add a word to the banned words list", aliases=["a"], pass_options=True
)
@lb.implements(lb.PrefixSubCommand)
async def censor_add(ctx: lb.Context, word: str) -> None:
    """Add a word to the censor list

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        word (str): The word to censor
    """

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        botdb = mod_plugin.bot.d.dbcon
        cur = botdb.cursor()

        cur.execute("INSERT INTO bannedwords VALUES (?) ", (word,))
        await ctx.respond(f"Adding word {word} to the banned words list")
        botdb.commit()
        await ctx.edit_last_response("Added to the banned words list")


@censor.child
@lb.option("word", "The word to remove")
@lb.command(
    "remove",
    "Add a word to the banned words list",
    aliases=["d", "delete", "del"],
    pass_options=True,
)
@lb.implements(lb.PrefixSubCommand)
async def censor_remove(ctx: lb.Context, word: str) -> None:
    """Remove a word from the censor list

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        word (str): The word to uncensor
    """
    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        botdb = mod_plugin.bot.d.dbcon
        cur = botdb.cursor()
        cur.execute("DELETE from bannedwords WHERE word= (?) ", (word,))

        await ctx.respond("Removing word from the banned words list")
        botdb.commit()
        await ctx.edit_last_response(f"Removed {word} from the banned words list")


# Listeners for the bot and firing of corresponding events


@mod_plugin.listener(hk.GuildMessageCreateEvent)
async def banned_words(event: hk.GuildMessageCreateEvent) -> None:
    """Listen to instances of banned words and delete if so"""

    if event.is_bot:
        return
    cur = mod_plugin.bot.d.dbcon.cursor()
    query = "SELECT * FROM bannedwords"
    cur.execute(query)
    banned_words = cur.fetchall()
    for word in banned_words:
        if word[0] in event.message.content.lower():
            await event.message.respond(
                f"Don't use banned words {hk.Emoji.parse('<:basedhalt:1013332614708461658>')}",
                reply=event.message,
                mentions_reply=True,
                flags=hk.MessageFlag.EPHEMERAL,
            )
            await event.message.delete()


@mod_plugin.listener(hk.MemberCreateEvent)
async def preban(event: hk.MemberCreateEvent):
    """Preban hook to be executed when a user joins the server"""

    cur = mod_plugin.bot.d.dbcon.cursor()
    query = "SELECT * FROM prebannedusers WHERE userid=?"
    args = (event.member.id,)
    cur.execute(query, args)
    banid = cur.fetchone()
    if banid:
        if not event.member.is_bot:
            await event.member.send(
                f"You are banned from the server: **{event.get_guild().name}**"
            )
        await event.member.ban()
        # channels = await mod_plugin.bot.rest.fetchchann (event.guild_id)
        await mod_plugin.bot.rest.create_message(
            980479966389096460, f"Banned the user `{event.member}` (preban)"
        )
        # await event.member.send(f"You were banned from `{ctx.get_guild()}` for `{reason}`")

    # if event.user_id in bannedUsers:
    # mod_plugin.bot.


@mod_plugin.listener(hk.GuildThreadCreateEvent)
async def join_thread(event: hk.GuildThreadCreateEvent):
    """Join a thread upon creation"""

    await mod_plugin.bot.rest.join_thread(event.thread_id)


# @mod_plugin.listener(hk.MessageDeleteEvent)
# async def sniper(event: hk.MessageDeleteEvent):
#     if event.is_bot:
#         return

#     # raise NotImplementedError
#     return

# THIS FUNCTION IS ARCHIVED FOR THE ONE IN LOG

# message = event.old_message

# if message.author.is_bot:
#     return

# embedColor = 0x000000
# # async for role in (await message.author.fetch_roles())[::-1]:
# #     if role.color != hk.Color(0x000000):
# #         embedColor = role.color
# await mod_plugin.bot.rest.create_message(
#     channel=event.old_message.channel_id,
#     # content=f"message {message.content} by {message.author} {message.author.avatar_url}",
#     embed=hk.Embed(
#         description=message.content, color=embedColor, timestamp=message.timestamp
#     ).set_author(name=f"{message.author}", icon=message.author.avatar_url),
# )
# # await mod_plugin.bot.rest.create_message(
# #     channel=message.channel_id,
# #     embed=hk.Embed(
# #         description=message.content, timestamp=message.timestamp
# #     )
# #     .set_author(name=message.author, icon=message.author.default_avatar_url),
# #     attachments=message.attachments
# # )

# await message.context.respond(


@purge.set_error_handler
async def on_purge_error(event: lb.CommandErrorEvent) -> bool:
    """Exception Handler"""
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lb.MissingRequiredPermission):
        await event.context.respond(
            f"Missing permissions {hk.Emoji.parse('<:worry:1061307106399113216>')}"
        )
        return True

    if isinstance(exception, lb.BotMissingRequiredPermission):
        await event.context.respond("I don't have the permissions to do this 😔")
        return True

    if isinstance(exception, isodate.isoerror.ISO8601Error):
        await event.context.respond("Couldn't parse time duration.")
        return True

    if isinstance(exception, lb.CommandIsOnCooldown):
        await event.context.respond(
            f"The command is on cooldown, you can use it after {int(exception.retry_after)}s",
            delete_after=int(exception.retry_after),
        )
        return True

    if isinstance(exception, hk.errors.BadRequestError):
        await event.context.respond(
            "You can only delete messages under 14 days old", delete_after=3
        )
        return True

    if isinstance(exception, lb.errors.NotEnoughArguments):
        await event.context.respond(
            "Kindly specify the number of messages to be deleted", delete_after=3
        )
        return True

    # use a webhook for this?
    if isinstance(exception, hk.errors.ForbiddenError):
        await event.context.respond("Error: Can't DM this user.")

    return False


lock_channel.set_error_handler(on_purge_error)
lock_server.set_error_handler(on_purge_error)
ban_user.set_error_handler(on_purge_error)
kick_user.set_error_handler(on_purge_error)
unban_user.set_error_handler(on_purge_error)
hide_channel.set_error_handler(on_purge_error)


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(mod_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(mod_plugin)
