"""Make cool plot charts"""
import io
from PIL import Image

import hikari as hk
import lightbulb as lb


import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from extPlugins.plot_curves2 import search_it


plot_plugin = lb.Plugin(
    "plot", "A set of commands that are used to plot anime's trends"
)


@plot_plugin.command
@lb.add_cooldown(7, 1, lb.UserBucket)
@lb.add_cooldown(20, 2, lb.ChannelBucket)
@lb.command("plot", "Make a series' trends' graph when it aired", aliases=["p"])
@lb.implements(lb.PrefixCommandGroup, lb.SlashCommandGroup)
async def plt_grp(ctx: lb.Context) -> None:
    """Base ftn to plot a graph"""


@plt_grp.child
@lb.option(
    "series",
    "The series whose trends to look for",
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.command(
    "trend",
    "Plot some trendz",
    pass_options=True,
    auto_defer=True,
    aliases=["t", "trends"],
)
@lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
async def plot_airing_trend(ctx: lb.Context, series: str) -> None:
    """Plot the popularity of an anime when it aired

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        series (str): Name of the series
    """
    data = await search_it(series)

    if isinstance(data, int):
        await ctx.respond(f"An error occurred, `code: {data}` ")
        return
    print(type(data))

    pio.renderers.default = "notebook"
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=data["data"][0],
            y=data["data"][1],
            mode="lines",
            name="Trends",
            line={"color": "MediumTurquoise", "width": 2.5},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["data"][2],
            y=data["data"][3],
            mode="markers",
            name="Episodes",
            line={"color": "MediumTurquoise", "width": 2.5},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["data"][4],
            y=data["data"][5],
            line={"color": "DeepPink"},
            name="Scores",
            mode="lines",
            line_shape="spline",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title=f'Series Trends: {data["name"]}',
        xaxis_title="Dates",
        yaxis_title="Trend Value",
        template="plotly_dark",
    )

    fig.update_yaxes(title_text="Score", secondary_y=True)
    img_bytes = fig.to_image(format="png")
    Image.open(io.BytesIO(img_bytes)).save(f"pictures/{series}.png")
    await ctx.respond(
        content=hk.Emoji.parse("<:nerd2:1060639499505377320>"),
        attachment=f"pictures/{series}.png",
    )


@plt_grp.child
@lb.option(
    "query",
    "The names of the series to compare",
    modifier=lb.commands.OptionModifier.CONSUME_REST,
)
@lb.command(
    "compare", "Plot some trendz", pass_options=True, auto_defer=True, aliases=["c"]
)
@lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
async def compare_trends(ctx: lb.Context, query: str) -> None:
    """Compare the popularity and ratings of two different anime

    Args:
        ctx (lb.Context): The event context (irrelevant to the user)
        query (str): The name of the two anime (seperated by "vs")
    """

    series = query.split("vs")
    if not len(series) != 2:
        await ctx.respond("Only 2 allowed rn")
        return

    async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
        data = await search_it(series[0])
        # from pprint import pprint
        data2 = await search_it(series[1])

        # await ctx.respond(f"{data, data2}")

        # pprint(data)
        # if type(data) or type(data2) == int:
        #     await ctx.respond(f"An error occurred, `code: {data}` ")
        #     return
        # print(type(data))

        pio.renderers.default = "notebook"
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=data["data"][0],
                y=data["data"][1],
                mode="lines",
                name=f"Trends {series[0]}",
                line={"color": "MediumTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][2],
                y=data["data"][3],
                mode="markers",
                name=f"Episodes {series[0]}",
                line={"color": "DarkTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][4],
                y=data["data"][5],
                line={"color": "DeepPink"},
                name=f"Scores {series[0]}",
                mode="lines",
                line_shape="spline",
            ),
            secondary_y=True,
        )

        # Second series
        fig.add_trace(
            go.Scatter(
                x=data2["data"][0],
                y=data2["data"][1],
                mode="lines",
                name=f"Trends {series[1]}",
                line={"color": "MediumSlateBlue", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data2["data"][2],
                y=data2["data"][3],
                mode="markers",
                name=f"Episodes {series[1]}",
                line={"color": "MediumSlateBlue", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data2["data"][4],
                y=data2["data"][5],
                line={"color": "DarkOrchid"},
                name=f"Scores {series[1]}",
                mode="lines",
                line_shape="spline",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title=f'Trends Comparision: {data["name"]} vs {data2["name"]}',
            xaxis_title="Dates",
            yaxis_title="Trend Value",
            template="plotly_dark",
        )

        fig.update_yaxes(title_text="Score", secondary_y=True)
        img_bytes = fig.to_image(format="png")
        Image.open(io.BytesIO(img_bytes)).save(f"pictures/{query}.png")
        await ctx.respond(
            content=hk.Emoji.parse("<:nerd2:1060639499505377320>"),
            attachment=f"pictures/{query}.png",
        )


# @fun_group.child
# @lb.command("animal2", "get an animaru uwu")
# @lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
# async def give_animal(ctx: lb.Context) -> None:
#     view = AnimalView(ctx.author)
#     resp = await ctx.respond(
#        "Pick an animal", components=view.build()
#     )
#     msg = await resp.message()
#     await view.start(msg)
#     await view.wait()
#     ctx.get_channel().pin

# @fun_group.child
# @lb.command("joke", "Fetch some joks")
# @lb.implements(lb.PrefixSubCommand, lb.SlashSubCommand)
# async def joke_reddit(ctx: lb.Context) ->None:
#
#     #Fetch memes from r/jokes or r/dadjokes (consider adding comments too?)
#     ...


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(plot_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(plot_plugin)
