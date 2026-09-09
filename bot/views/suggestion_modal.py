import discord


class CommentModal(
    discord.ui.Modal,
    title="Add Suggestion",
):

    suggestion = discord.ui.TextInput(
        label="Suggestion",
        placeholder="Write your suggestion...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    def __init__(
        self,
        submission_message_id: int,
    ):
        super().__init__()

        self.submission_message_id = submission_message_id

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        # ----------------------------------------------------
        # GET CHANNEL
        # ----------------------------------------------------

        channel = interaction.channel

        if channel is None:

            await interaction.response.send_message(
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

            await interaction.response.send_message(
                "❌ The original submission message could not be found.",
                ephemeral=True,
            )

            return

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I don't have permission to access the submission message.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # ADD SUGGESTION AS REPLY
        # ----------------------------------------------------

        try:

            await submission_message.reply(
                content=(
                    f"💡 **Suggestion from "
                    f"{interaction.user.mention}**\n\n"
                    f"{self.suggestion.value}"
                )
            )

        except Exception:

            await interaction.response.send_message(
                "❌ Something went wrong while adding the suggestion.",
                ephemeral=True,
            )

            return

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        await interaction.response.send_message(
            "✅ Suggestion added.",
            ephemeral=True,
        )