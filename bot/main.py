"""
Application entry point for the Discord employee updates bot.

This module initializes the Discord client, registers application
commands and persistent views, handles command errors, and starts
the bot.
"""

import asyncio
import logging

from discord import Client, Interaction, Intents, app_commands
from discord.errors import HTTPException

from bot.commands.submission import submit_group
from bot.views.submission_view import SubmissionView
from config.settings import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


class EmployeeUpdatesBot(Client):
    """Discord client for the employee updates application."""

    def __init__(self) -> None:
        """Initialize the Discord client and application command tree."""

        super().__init__(
            intents=Intents.default(),
        )

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """Register commands and persistent views, then sync commands."""

        self.tree.add_command(submit_group)

        self.add_view(
            SubmissionView(),
        )

        await self.tree.sync()

        logger.info(
            "Slash commands synced successfully.",
        )


bot = EmployeeUpdatesBot()


@bot.event
async def on_ready() -> None:
    """Log when the bot successfully connects to Discord."""

    logger.info(
        "Logged in as %s.",
        bot.user,
    )


@bot.tree.error
async def on_app_command_error(
    interaction: Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Handle unhandled application-command errors."""

    logger.error(
        "Unhandled application command error: %s",
        error,
        exc_info=(type(error), error, error.__traceback__),
    )

    error_message = (
        "❌ Something went wrong while processing your command. "
        "Please try again later."
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                error_message,
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                error_message,
                ephemeral=True,
            )

    except HTTPException:
        logger.exception(
            "Failed to send the application-command error response.",
        )

    except Exception:
        logger.exception(
            "Unexpected error while sending the application-command "
            "error response.",
        )


async def main() -> None:
    """Start and manage the Discord bot lifecycle."""

    async with bot:
        await bot.start(
            settings.discord_bot_token,
        )


if __name__ == "__main__":
    # Psycopg async mode requires a selector-based event loop on Windows.
    asyncio.run(
        main(),
        loop_factory=asyncio.SelectorEventLoop,
    )