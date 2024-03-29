"""Plugin to make/deal with webhooks"""
import hikari as hk
import lightbulb as lb


webhook_plugin = lb.Plugin("Webhook", "Utilize webhooks")


@webhook_plugin.command
@lb.option(
    "message", "Message to say", str, modifier=lb.commands.OptionModifier.CONSUME_REST
)
@lb.option("user", "User to say it as", hk.Member)
@lb.command("impostor", "Make a webhook", pass_options=True, aliases=["i"])
@lb.implements(lb.PrefixCommand)
async def impostor(ctx: lb.Context, user: hk.Member, message: str) -> None:
    """Say a message as someone else 😈

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        user (hk.Member): The user to say it as
        message (str): The message to say
    """

    if isinstance(ctx, lb.PrefixContext):
        await ctx.event.message.delete()
    webhook = await webhook_plugin.bot.rest.create_webhook(
        channel=ctx.channel_id, name=user.username
    )
    await webhook.execute(
        content=message, avatar_url=user.avatar_url, user_mentions=True
    )
    await webhook_plugin.bot.rest.delete_webhook(webhook)


@webhook_plugin.set_error_handler
async def compile_error(event: lb.CommandErrorEvent) -> bool:
    """Error handler"""
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lb.MissingRequiredPermission):
        await event.context.respond("You're missing some perms there, bub.")
        return True

    if isinstance(exception, lb.CommandIsOnCooldown):
        await event.context.respond(
            f"The command is on cooldown, you can use it after {int(exception.retry_after)}s",
            delete_after=int(exception.retry_after),
        )
        return True

    if isinstance(exception, lb.errors.NotEnoughArguments):
        await event.context.respond(
            "Kindly specify the number of messages to be deleted", delete_after=3
        )
        return True

    return False


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(webhook_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(webhook_plugin)
