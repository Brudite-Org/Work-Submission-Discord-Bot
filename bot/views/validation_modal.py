import discord

from app.services.submission_service import (
    get_submission_by_message_id,
    get_submission_validations,
    validate_submission,
)
from config.database import SessionLocal

from bot.views.submission_view import SubmissionView


class ValidationModal(
    discord.ui.Modal,
    title="Validate Submission",
):

    note = discord.ui.TextInput(
        label="Validation note (optional)",
        placeholder="Add a note if you want...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000,
    )

    def __init__(
        self,
        submitter_id: int,
        submission_message_id: int,
    ):
        super().__init__()

        self.submitter_id = submitter_id
        self.submission_message_id = submission_message_id

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        # ----------------------------------------------------
        # SECURITY CHECK 1
        # ----------------------------------------------------

        validator_role = discord.utils.get(
            interaction.user.roles,
            name="Validator",
        )

        if validator_role is None:

            await interaction.response.send_message(
                "❌ You do not have permission to validate submissions.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # SECURITY CHECK 2
        # ----------------------------------------------------

        if interaction.user.id == self.submitter_id:

            await interaction.response.send_message(
                "❌ You cannot validate your own submission.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # ACKNOWLEDGE MODAL
        # ----------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )

        # ----------------------------------------------------
        # GET CHANNEL
        # ----------------------------------------------------

        channel = interaction.channel

        if channel is None:

            await interaction.followup.send(
                "❌ Could not find the submission channel.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # GET ORIGINAL SUBMISSION MESSAGE
        # ----------------------------------------------------

        try:

            submission_message = await channel.fetch_message(
                self.submission_message_id
            )

        except discord.NotFound:

            await interaction.followup.send(
                "❌ The original submission message could not be found.",
                ephemeral=True,
            )

            return

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I don't have permission to access the submission message.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # DATABASE OPERATION
        # ----------------------------------------------------

        db = SessionLocal()

        try:

            # ----------------------------------------------
            # Find submission using Discord message ID
            # ----------------------------------------------

            submission = get_submission_by_message_id(
                db=db,
                message_id=self.submission_message_id,
            )

            # ----------------------------------------------
            # Create validation record
            # ----------------------------------------------

            validate_submission(
                db=db,
                submission_id=submission.id,
                validator_id=interaction.user.id,
                validation_note=self.note.value.strip() or None,
            )

            # ----------------------------------------------
            # Get ALL validations for this submission
            # ----------------------------------------------

            validations = get_submission_validations(
                db=db,
                submission_id=submission.id,
            )

        except ValueError as error:

            db.rollback()

            await interaction.followup.send(
                f"❌ {error}",
                ephemeral=True,
            )

            return

        except Exception:

            db.rollback()

            await interaction.followup.send(
                "❌ Something went wrong while validating the submission.",
                ephemeral=True,
            )

            raise

        finally:

            db.close()

        # ----------------------------------------------------
        # CHECK EMBED
        # ----------------------------------------------------

        if not submission_message.embeds:

            await interaction.followup.send(
                "⚠️ The submission was validated in the database, "
                "but the Discord message has no embed to update.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # COPY ORIGINAL EMBED
        # ----------------------------------------------------

        embed = submission_message.embeds[0].copy()

        # ----------------------------------------------------
        # REMOVE OLD VALIDATION FIELDS
        # ----------------------------------------------------

        fields_to_keep = []

        for field in embed.fields:

            if field.name in (
                "Validated By",
                "Validation Note",
                "Validations",
            ):
                continue

            fields_to_keep.append(field)

        # Rebuild embed fields.

        new_embed = discord.Embed.from_dict(
            embed.to_dict()
        )

        new_embed.clear_fields()

        for field in fields_to_keep:

            new_embed.add_field(
                name=field.name,
                value=field.value,
                inline=field.inline,
            )

        embed = new_embed

        # ----------------------------------------------------
        # FIND STATUS FIELD
        # ----------------------------------------------------

        status_index = None

        for index, field in enumerate(embed.fields):

            if field.name == "Status":

                status_index = index

                break

        # ----------------------------------------------------
        # UPDATE STATUS
        # ----------------------------------------------------

        if status_index is not None:

            embed.set_field_at(
                status_index,
                name="Status",
                value="🟢 Validated",
                inline=False,
            )

        # ----------------------------------------------------
        # BUILD VALIDATION SUMMARY
        # ----------------------------------------------------

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
            validation_lines
        )

        # ----------------------------------------------------
        # ADD ALL VALIDATIONS
        # ----------------------------------------------------

        if validation_summary:

            # Discord embed fields have a 1024-character
            # value limit.

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

        # ----------------------------------------------------
        # UPDATE ORIGINAL SUBMISSION MESSAGE
        # ----------------------------------------------------

        await submission_message.edit(
            embed=embed,
            view=SubmissionView(
                submitter_id=self.submitter_id,
                validated=True,
            ),
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        await interaction.followup.send(
            "✅ Your validation has been recorded.",
            ephemeral=True,
        )