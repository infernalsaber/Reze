import hikari as hk
import lightbulb as lb

import random

welcome = lb.Plugin("Welcome", "Welcoming a newbie")

welcome_pics = [
    "http://i.imgur.com/0AGYhqM.jpg",
    "https://i.imgur.com/x0pqPxx.jpg",
    "https://i.imgur.com/RGHfu42.jpg",
    "https://i.imgur.com/IVWa2Ml.jpg",
    "https://i.imgur.com/FmVE1HW.jpg",
    "https://soranews24.com/wp-content/uploads/sites/3/2014/05/ssom.jpg"
]


@welcome.listener(hk.GuildJoinEvent)
async def welcome_ftn(event: hk.GuildJoinEvent) -> None:
    
    welcome_embed = hk.Embed(
        
        title=f"Welcome to the {event.fetch_guild().name} server",
        content = "• Remember to follow rules and stuff \
            \n• Behave like a normal human being \
            \n• Enjoy",
        color= 0xf4eae9,
    ).set_image(random.choice(welcome_pics))
    
    welcome.bot.rest.create_message(channel, welcome_embed)



def load(bot: lb.BotApp) -> None:
    bot.add_plugin(welcome)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(welcome)