from extPlugins.misc import GenericButton, KillButton
import os

import lightbulb as lb
import hikari as hk
import miru


dir_plugin = lb.Plugin("Directory", "Access the bot's storage directory")

# from extensions.yt import GenericButton


@dir_plugin.command
@lb.command("dir", "Upload media files from the cwd", pass_options=True)
@lb.implements(lb.PrefixCommand)
async def directory(ctx: lb.Context) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    embed = hk.Embed()
    view = miru.View()

    for i, item in enumerate(["videos", "pictures", "arts"]):
        embed.add_field(f"`{i+1}.`", f"```ansi\n\u001b[0;35m{item} ```")
        view.add_item(GenericButton(style=hk.ButtonStyle.SECONDARY, label=str(item)))
    view.add_item(KillButton(style=hk.ButtonStyle.DANGER, label="❌"))

    choice = await ctx.respond(embed=embed, components=view)

    await view.start(choice)
    await view.wait()

    if not hasattr(view, "answer"):
        await ctx.edit_last_response("Process timed out", embeds=[], components=[])
        return

    folder = view.answer

    # view.remove_item(item)

    embed2 = hk.Embed()
    view2 = miru.View()

    for i, item in enumerate(os.listdir(f"./{folder}")):
        embed2.add_field(f"`{i+1}.`", f"```ansi\n\u001b[0;35m{item} ```")

        view2.add_item(GenericButton(style=hk.ButtonStyle.SECONDARY, label=f"{i+1}"))
    view2.add_item(KillButton(style=hk.ButtonStyle.DANGER, label="❌"))
    # view.

    # view.add_item(NoButton(style=hk.ButtonStyle.DANGER, label="No"))
    choice = await ctx.edit_last_response(embed=embed2, components=view2)

    await view2.start(choice)
    await view2.wait()
    # view.from_message(message)
    if hasattr(view2, "answer"):  # Check if there is an answer
        await ctx.edit_last_response(content="Here it is.", embeds=[], components=[])
        filez = os.listdir(f"./{folder}")[int(view2.answer) - 1]
    else:
        await ctx.edit_last_response("Process timed out.", embeds=[], components=[])
        return
        # return
    await ctx.respond(attachment=f"{folder}/{filez}")

    # if lstVids[vidIndex].get_duration_secs() < 60 or lstVids[vidIndex].get_duration_secs() > 601:
    #     await ctx.respond("Invalid time duration.")
    #     return


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(dir_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(dir_plugin)
