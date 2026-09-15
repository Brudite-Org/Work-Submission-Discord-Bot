"""
Discord views for interacting with employee work submissions.
"""

import logging
from typing import TYPE_CHECKING

from discord import (
    ButtonStyle,
    Interaction,
    Member,
    ui,
)
from sqlalchemy.exc import SQLAlchemyError

from app.services.submission_service import (
    get_submission_by_message_id,
)
from bot.views.suggestion_modal import CommentModal
from config.database import async_session_factory
from config.settings import settings


if TYPE_CHECKING:
    from bot.views.validation_modal import ValidationModal


logger = logging.getLogger(__name__)


def has_validator_role(member: Member) -> bool:
    """Return whether a member has the configured validator role."""

    return any(
        role.id == settings.validator_role_id
        for role in member.roles
    )


class ActionView(ui.View):
    """Provide actions available for the interacting user."""

    def __init__(
        self,
        submitter_id: int,
        submission_message_id: int,
        can_validate: bool,
    ) -> None:
        super().__init__(
            timeout=300,
        )

        self.submitter_id = submitter_id
        self.submission_message_id = submission_message_id

        if can_validate:
            self.add_item(
                ValidateButton(
                    submitter_id=submitter_id,
                    submission_message_id=submission_message_id,
                )
            )

    @ui.button(
        label="💡 Add Suggestion",
        style=ButtonStyle.secondary,
    )
    async def suggestion_button(
        self,
        interaction: Interaction,
        button: ui.Button,
    ) -> None:
        """Open the suggestion modal."""

        await interaction.response.send_modal(
            CommentModal(
                submission_message_id=self.submission_message_id,
            )
        )


class ValidateButton(ui.Button):
    """Provide the validation action to eligible validators."""

    def __init__(
        self,
        submitter_id: int,
        submission_message_id: int,
    ) -> None:
        super().__init__(
            label="✅ Validate Submission",
            style=ButtonStyle.success,
        )

        self.submitter_id = submitter_id
        self.submission_message_id = submission_message_id

    async def callback(
        self,
        interaction: Interaction,
    ) -> None:
        """Open the validation modal for an eligible validator."""

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

        from bot.views.validation_modal import ValidationModal

        await interaction.response.send_modal(
            ValidationModal(
                submitter_id=self.submitter_id,
                submission_message_id=self.submission_message_id,
            )
        )


class SubmissionView(ui.View):
    """Provide the persistent public action button for a submission."""

    def __init__(self) -> None:
        super().__init__(
            timeout=None,
        )

    @ui.button(
        label="⚙️ Open Actions",
        style=ButtonStyle.secondary,
        custom_id="submission:open_actions",
    )
    async def open_actions(
        self,
        interaction: Interaction,
        button: ui.Button,
    ) -> None:
        """Open an action panel appropriate for the interacting user."""

        if not isinstance(interaction.user, Member):
            await interaction.response.send_message(
                "❌ Could not verify your server permissions.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(
            ephemeral=True,
        )

        try:
            async with async_session_factory() as db:
                submission = await get_submission_by_message_id(
                    db=db,
                    message_id=interaction.message.id,
                )

        except ValueError:
            logger.warning(
                "Submission not found for Discord message ID %s.",
                interaction.message.id,
            )

            await interaction.followup.send(
                "❌ This submission could not be found.",
                ephemeral=True,
            )
            return

        except SQLAlchemyError:
            logger.exception(
                "Database error while opening submission actions.",
            )

            await interaction.followup.send(
                "❌ A database error occurred while opening "
                "the submission actions.",
                ephemeral=True,
            )
            return

        except Exception:
            logger.exception(
                "Unexpected error while opening submission actions.",
            )

            await interaction.followup.send(
                "❌ An unexpected error occurred. Please try again later.",
                ephemeral=True,
            )
            return

        can_validate = (
            has_validator_role(interaction.user)
            and interaction.user.id != submission.employee_id
        )

        await interaction.followup.send(
            "Choose an action:",
            view=ActionView(
                submitter_id=submission.employee_id,
                submission_message_id=interaction.message.id,
                can_validate=can_validate,
            ),
            ephemeral=True,
        )