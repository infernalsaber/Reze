# import os, lxml, re, json, urllib.request, requests
# from bs4 import BeautifulSoup
# from PIL import Image

# from typing import Optional

import hikari as hk
import lightbulb as lb

# import miru
# from miru.ext import nav

import subprocess


compiler_plugin = lb.Plugin("Compiler", "An interpreter for Python")

dscSyntaxGist = "https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51#syntax-highlighting"

# import time


@compiler_plugin.command
@lb.option(
    "code", "The code to test", str, modifier=lb.commands.OptionModifier.CONSUME_REST
)
@lb.add_checks(lb.owner_only)
@lb.command(
    "e",
    "Test some code and see output/errors (python)",
    pass_options=True,
    aliases=["py", "exec"],
)
@lb.implements(lb.PrefixCommand)
async def compiler(ctx: lb.Context, code: str) -> None:
    if not (code.startswith("```py") and code.endswith("```")):
        await ctx.respond(
            f"The entered code is not formatted correctly according to python. Consider referring : {hk.URL(dscSyntaxGist)}."
        )
        return
    # print(code[5:-3])
    # codeBlock = "".join(code[1:]).replace(";", "\n").replace("```", "")
    # print(codeBlock)
    with open("ntfc.py", "w") as f:
        f.write(code[5:-3])

    result = subprocess.Popen(
        ["python3", "ntfc.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = result.communicate(timeout=12)
    print(output, error)
    if error:
        await ctx.respond(
            f"Process returned with error: ```{(str(error, 'UTF-8')).split('ntfc.py')[1][3:]}```"
        )
    else:
        if not output:
            # await ctx.respond("Yamete")
            await ctx.respond(f"This is the output ```        ```")
        else:
            # a = (str(output, 'UTF-8'))
            await ctx.respond(f"This is the output ```ansi\n{str(output, 'UTF-8')}```")
            # await ctx.respond(a)


@compiler_plugin.command
@lb.add_checks(lb.owner_only)
@lb.option(
    "query", "The queries to run", str, modifier=lb.commands.OptionModifier.CONSUME_REST
)
@lb.command("dbm", "Modify the database", pass_options=True, aliases=["sql"])
@lb.implements(lb.PrefixCommand)
async def compiler(ctx: lb.Context, code: str) -> None:
    raise NotImplementedError
    return
    if not (code.startswith("```sql") and code.endswith("```")):
        await ctx.respond(
            f"The entered code is not formatted correctly according to sql. Consider referring : {hk.URL(dscSyntaxGist)}."
        )
        return
    botdb = ctx.bot.d.dbcon

    c = botdb.cursor()
    c.execute(query[6:-3])
    res = c.fetchall()
    if res:
        await ctx.respond("f```{res}```")

    result = subprocess.Popen(
        ["python", "ntfc.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = result.communicate()
    print(output, error)
    if error:
        await ctx.respond(
            f"Process returned with error: ```{(str(error, 'UTF-8')).split('ntfc.py')[1][3:]}```"
        )
    else:
        if not output:
            await ctx.respond(f"This is the output ```        ```")
        else:
            # a = (str(output, 'UTF-8'))
            await ctx.respond(f"This is the output ```ansi\n{str(output, 'UTF-8')}```")


@compiler.set_error_handler
async def compile_error(event: lb.CommandErrorEvent) -> bool:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lb.MissingRequiredPermission):
        await event.context.respond("You're missing some perms there, bub.")
        return True

    elif isinstance(exception, lb.CommandIsOnCooldown):
        await event.context.respond(
            f"The command is on cooldown, you can use it after {int(exception.retry_after)}s",
            delete_after=int(exception.retry_after),
        )
        return True

    elif isinstance(exception, lb.errors.NotEnoughArguments):
        await event.context.respond(
            "Kindly specify the number of messages to be deleted", delete_after=3
        )
        return True

    return False


def load(bot: lb.BotApp) -> None:
    bot.add_plugin(compiler_plugin)


def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(compiler_plugin)
