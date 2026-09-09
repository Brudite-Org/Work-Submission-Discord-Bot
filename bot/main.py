import discord
from discord import app_commands

from bot.commands.submission import submit_group
from config.settings import settings


# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()

bot = discord.Client(
    intents=intents
)

tree = app_commands.CommandTree(bot)


# ============================================================
# COMMAND REGISTRATION
# ============================================================

tree.add_command(
    submit_group
)


# ============================================================
# BOT READY
# ============================================================

@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )

    await tree.sync()

    print(
        "Slash commands synced."
    )


# ============================================================
# START BOT
# ============================================================

bot.run(
    settings.discord_bot_token
)