import discord

from bot.views.suggestion_modal import CommentModal


class NormalActionView(
    discord.ui.View
):

    def __init__(
        self,
        submission_message_id: int,
    ):
        super().__init__(
            timeout=300
        )

        self.submission_message_id = submission_message_id

    @discord.ui.button(
        label="💡 Add Suggestion",
        style=discord.ButtonStyle.secondary,
    )
    async def suggestion_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):

        await interaction.response.send_modal(
            CommentModal(
                submission_message_id=self.submission_message_id
            )
        )


class ValidatorActionView(
    discord.ui.View
):

    def __init__(
        self,
        submitter_id: int,
        submission_message_id: int,
    ):
        super().__init__(
            timeout=300
        )

        self.submitter_id = submitter_id
        self.submission_message_id = submission_message_id

    @discord.ui.button(
        label="💡 Add Suggestion",
        style=discord.ButtonStyle.secondary,
    )
    async def suggestion_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):

        await interaction.response.send_modal(
            CommentModal(
                submission_message_id=self.submission_message_id
            )
        )

    @discord.ui.button(
        label="✅ Validate Submission",
        style=discord.ButtonStyle.success,
    )
    async def validate_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):


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


class SubmissionView(
    discord.ui.View
):

    def __init__(
        self,
        submitter_id: int,
        validated: bool = False,
    ):
        super().__init__(
            timeout=None
        )

        self.submitter_id = submitter_id
        self.validated = validated

    @discord.ui.button(
        label="⚙️ Open Actions",
        style=discord.ButtonStyle.secondary,
    )
    async def open_actions(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):


        validator_role = discord.utils.get(
            interaction.user.roles,
            name="Validator",
        )


        if (
            validator_role is not None
            and interaction.user.id != self.submitter_id
        ):

            await interaction.response.send_message(
                "Choose an action:",
                view=ValidatorActionView(
                    submitter_id=self.submitter_id,
                    submission_message_id=interaction.message.id,
                ),
                ephemeral=True,
            )

            return


        await interaction.response.send_message(
            "Choose an action:",
            view=NormalActionView(
                submission_message_id=interaction.message.id
            ),
            ephemeral=True,
        )