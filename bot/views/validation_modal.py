"""
Discord modal for validating employee work submissions.
"""

import logging

from discord import (
    Forbidden,
    HTTPException,
    Interaction,
    Member,
    NotFound,
    TextStyle,
    ui,
)
from sqlalchemy.exc import SQLAlchemyError

from app.services.submission_service import (
    get_submission_by_message_id,
    get_submission_validations,
    validate_submission,
)
from bot.views.submission_view import (
    SubmissionView,
    has_validator_role,
)
from config.database import async_session_factory


logger = logging.getLogger(__name__)


class ValidationModal(
    ui.Modal,
    title="Validate Submission",
):
    """Provide a modal for validators to validate submissions."""

    note = ui.TextInput(
        label="Validation note (optional)",
        placeholder="Add a note if you want...",
        style=TextStyle.paragraph,
        required=False,
        max_length=1000,
    )

    def __init__(
        self,
        submitter_id: int,
        submission_message_id: int,
    ) -> None:
        super().__init__()

        self.submitter_id = submitter_id
        self.submission_message_id = submission_message_id

    async def on_submit(
        self,
        interaction: Interaction,
    ) -> None:
        """Validate the submission and update its Discord message."""

        if not isinstance(interaction.user, Member):
            await interaction.response.send_message(
                "❌ Could not verify your server permissions.",
                ephemeral=True,
            )
            return

        if not has_validator_role(interaction.user):
            await interaction.response.send_message(
                "❌ You do not have permission to validate submissions.",
                ephemeral=True,
            )
            return

        if interaction.user.id == self.submitter_id:
            await interaction.response.send_message(
                "❌ You cannot validate your own submission.",
                ephemeral=True,
            )
            return

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
            async with async_session_factory() as db:
                submission = await get_submission_by_message_id(
                    db=db,
                    message_id=self.submission_message_id,
                )

                submission_id = submission.id

                await validate_submission(
                    db=db,
                    submission_id=submission_id,
                    validator_id=interaction.user.id,
                    validation_note=self.note.value.strip() or None,
                )

                validations = await get_submission_validations(
                    db=db,
                    submission_id=submission_id,
                )

        except ValueError as error:
            logger.warning(
                "Validation rejected for submission %s: %s",
                self.submission_message_id,
                error,
            )

            await interaction.followup.send(
                f"❌ {error}",
                ephemeral=True,
            )
            return

        except SQLAlchemyError:
            logger.exception(
                "Database error while validating submission %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ A database error occurred while validating "
                "the submission. Please try again.",
                ephemeral=True,
            )
            return

        except Exception:
            logger.exception(
                "Unexpected error while validating submission %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "❌ An unexpected error occurred. Please try again later.",
                ephemeral=True,
            )
            return

        if not submission_message.embeds:
            logger.error(
                "Submission message %s has no embed.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "⚠️ The submission was validated in the database, "
                "but the Discord message has no embed to update.",
                ephemeral=True,
            )
            return

        embed = submission_message.embeds[0].copy()

        fields_to_keep = [
            field
            for field in embed.fields
            if field.name not in {
                "Validated By",
                "Validation Note",
                "Validations",
            }
        ]

        embed.clear_fields()

        for field in fields_to_keep:
            embed.add_field(
                name=field.name,
                value=field.value,
                inline=field.inline,
            )

        status_index = next(
            (
                index
                for index, field in enumerate(embed.fields)
                if field.name == "Status"
            ),
            None,
        )

        if status_index is None:
            embed.add_field(
                name="Status",
                value="🟢 Validated",
                inline=False,
            )
        else:
            embed.set_field_at(
                status_index,
                name="Status",
                value="🟢 Validated",
                inline=False,
            )

        validation_lines = []

        for validation in validations:
            validator = f"<@{validation.validator_id}>"

            if validation.validation_note:
                validation_lines.append(
                    f"👤 {validator}\n"
                    f"   {validation.validation_note}"
                )
            else:
                validation_lines.append(
                    f"👤 {validator}"
                )

        validation_summary = "\n\n".join(
            validation_lines,
        )

        if validation_summary:
            if len(validation_summary) > 1024:
                validation_summary = (
                    validation_summary[:1000]
                    + "\n..."
                )

            embed.add_field(
                name="Validations",
                value=validation_summary,
                inline=False,
            )

        try:
            await submission_message.edit(
                embed=embed,
                view=SubmissionView(),
            )

        except NotFound:
            logger.warning(
                "Submission message %s no longer exists.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "⚠️ The submission was validated, "
                "but the Discord message no longer exists.",
                ephemeral=True,
            )
            return

        except Forbidden:
            logger.exception(
                "Permission denied while updating submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "⚠️ The submission was validated, "
                "but I don't have permission to update the message.",
                ephemeral=True,
            )
            return

        except HTTPException:
            logger.exception(
                "Discord HTTP error while updating submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "⚠️ The submission was validated, "
                "but Discord could not update the message.",
                ephemeral=True,
            )
            return

        except Exception:
            logger.exception(
                "Unexpected error while updating submission message %s.",
                self.submission_message_id,
            )

            await interaction.followup.send(
                "⚠️ The submission was validated, "
                "but an unexpected error occurred while updating Discord.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Your validation has been recorded.",
            ephemeral=True,
        )