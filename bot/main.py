import discord
from discord import app_commands

from bot.commands.submission import submit_group
from config.settings import settings



#yha we are setting the bot up
intents = discord.Intents.default()

bot = discord.Client(
    intents=intents
)

tree = app_commands.CommandTree(bot)



#apna /command register kr rhe h
tree.add_command(
    submit_group
)


#jab discord ready  bol dega apne client ko t0w kya hoga
@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )
    #ye await se we are the /comands with discord
    await tree.sync()

    print(
        "Slash commands synced."
    )


#start the bowwt
bot.run(
    settings.discord_bot_token
)