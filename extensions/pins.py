import hikari as hk
import lightbulb as lb

pin_board = lb.Plugin("Pins", "Pin messages with >x 📌 reactions (wannabe starboard)")


@pin_board.listener(hk.GuildReactionAddEvent)
async def pin_lol(event: hk.GuildReactionAddEvent) -> None:
    # event.channel_id.pin_message(event.message)
    if not event.is_for_emoji("📌"):
        return

    message = await pin_board.bot.rest.fetch_message(event.channel_id, event.message_id)

    num_reaction = (
        [
            reaction
            for reaction in message.reactions
            if str(reaction.emoji.name) == event.emoji_name
        ][0]
    ).count
    # Sample Reaction: [Reaction(count=2, emoji='🔥')]

    # print(num_reaction)

    # WORKS
    if num_reaction == 2:
        await pin_board.bot.cache.get_guild_channel(event.channel_id).pin_message(
            event.message_id
        )

    # pin_board.bot.cache.getchannel(event.channel_id)


# @al_listener.listener(hk.GuildReactionAddEvent)
# async def pinner(event: hk.GuildReactionAddEvent) -> None:
#     ...


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(pin_board)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(pin_board)
