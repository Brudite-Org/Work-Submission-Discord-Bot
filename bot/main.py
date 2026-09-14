"""
Application entry point for the Discord bot.

This module initializes the Discord client, registers application
commands, synchronizes commands with Discord, and starts the bot.
"""

import asyncio
import logging

import discord
from discord import app_commands

from bot.commands.submission import submit_group
from bot.views.submission_view import SubmissionView
from config.settings import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


class EmployeeUpdatesBot(discord.Client):
    """Discord client for the employee updates bot."""

    def __init__(self) -> None:
        """Initialize the Discord client and command tree."""

        intents = discord.Intents.default()

        super().__init__(
            intents=intents,
        )

        self.tree = app_commands.CommandTree(
            self,
        )

    async def setup_hook(self) -> None:
        """Register commands and persistent Discord views."""

        self.tree.add_command(
            submit_group,
        )

        self.add_view(
            SubmissionView(),
        )

        await self.tree.sync()

        logger.info(
            "Slash commands synced.",
        )


bot = EmployeeUpdatesBot()


@bot.event
async def on_ready() -> None:
    """Handle the bot becoming ready after connecting to Discord."""

    logger.info(
        "Logged in as %s",
        bot.user,
    )


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Handle unexpected errors raised by application commands."""

    logger.error(
        "Application command error",
        exc_info=error,
    )

    message = (
        "❌ Something went wrong while processing your command. "
        "Please try again."
    )

    if interaction.response.is_done():
        await interaction.followup.send(
            message,
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True,
        )


async def main() -> None:
    """Start the Discord bot."""

    async with bot:
        await bot.start(
            settings.discord_bot_token,
        )


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=asyncio.SelectorEventLoop,
    )