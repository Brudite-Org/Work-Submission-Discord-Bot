"""
Discord modal for adding suggestions to employee work submissions.
"""

import logging

from discord import (
    Forbidden,
    HTTPException,
    Interaction,
    NotFound,
    TextStyle,
    ui,
)


logger = logging.getLogger(__name__)


class CommentModal(ui.Modal, title="Add Suggestion"):
    """Provide a modal for users to add suggestions to submissions."""

    suggestion = ui.TextInput(
        label="Suggestion",
        placeholder="Write your suggestion...",
        style=TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    def __init__(
        self,
        submission_message_id: int,
    ) -> None:
        super().__init__()

        self.submission_message_id = submission_message_id

    async def on_submit(
        self,
        interaction: Interaction,
    ) -> None:
        """Add the submitted suggestion as a reply to the submission."""

        await interaction.response.defer(
            ephemeral=True,
        )

        channel = interaction.channel

        if channel is None:
            await interaction.followup.send(
                "❌ Could not find the submission channel.",
                ephemeral=True,
            )
            return

        try:
            submission_message = await channel.fetch_message(
                self.submission_message_id,
            )

        except NotFound:
            logger.warning(
                "Submission message %s was not found.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ The original submission message could not be found.",
                ephemeral=True,
            )
            return

        except Forbidden:
            logger.exception(
                "Permission denied while fetching submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ I don't have permission to access the submission message.",
                ephemeral=True,
            )
            return

        except HTTPException:
            logger.exception(
                "Discord HTTP error while fetching submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ Discord could not retrieve the submission message.",
                ephemeral=True,
            )
            return

        except Exception:
            logger.exception(
                "Unexpected error while fetching submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ An unexpected error occurred. Please try again later.",
                ephemeral=True,
            )
            return

        try:
            await submission_message.reply(
                content=(
                    f"💡 **Suggestion from "
                    f"{interaction.user.mention}**\n\n"
                    f"{self.suggestion.value}"
                ),
            )

        except NotFound:
            logger.warning(
                "Submission message %s disappeared before replying.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ The original submission message could not be found.",
                ephemeral=True,
            )
            return

        except Forbidden:
            logger.exception(
                "Permission denied while replying to submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ I don't have permission to reply to the submission.",
                ephemeral=True,
            )
            return

        except HTTPException:
            logger.exception(
                "Discord HTTP error while adding suggestion.",
            )

            await interaction.followup.send(
                "❌ Discord could not add your suggestion. "
                "Please try again.",
                ephemeral=True,
            )
            return

        except Exception:
            logger.exception(
                "Unexpected error while adding suggestion.",
            )

            await interaction.followup.send(
                "❌ An unexpected error occurred. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Suggestion added.",
            ephemeral=True,
        )