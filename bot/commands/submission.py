import discord
from discord import app_commands

from app.services.submission_service import (
    create_submission,
    set_discord_message_id,
)
from bot.views.submission_view import SubmissionView
from config.database import SessionLocal


# ============================================================
# SUBMIT COMMAND GROUP
# ============================================================

submit_group = app_commands.Group(
    name="submit",
    description="Submit employee work updates",
)


# ============================================================
# /submit work
# ============================================================

@submit_group.command(
    name="work",
    description="Submit a work update",
)
@app_commands.describe(
    title="Title of your work update",
    description="Describe what you worked on",
    links="Useful links",
    attachment="Optional file or image",
)
async def submit_work(
    interaction: discord.Interaction,
    title: str,
    description: str | None = None,
    links: str | None = None,
    attachment: discord.Attachment | None = None,
):
    # --------------------------------------------------------
    # GET ATTACHMENT URL
    # --------------------------------------------------------

    attachment_url = None

    if attachment is not None:
        attachment_url = attachment.url

    # --------------------------------------------------------
    # CREATE DATABASE SUBMISSION
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        submission = create_submission(
            db=db,
            title=title,
            description=description,
            links=links,
            attachment_url=attachment_url,
            employee_id=interaction.user.id,
            channel_id=interaction.channel.id,
        )

    finally:
        db.close()

    # --------------------------------------------------------
    # BUILD DISCORD EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="📝 WORK UPDATE",
        color=discord.Color.orange(),
    )

    embed.add_field(
        name="Title",
        value=title,
        inline=False,
    )

    embed.add_field(
        name="👤 Employee",
        value=interaction.user.mention,
        inline=False,
    )

    embed.add_field(
        name="🕐 Timestamp",
        value=discord.utils.format_dt(
            discord.utils.utcnow(),
            style="F",
        ),
        inline=False,
    )

    # --------------------------------------------------------
    # OPTIONAL DESCRIPTION
    # --------------------------------------------------------

    if description:

        embed.add_field(
            name="📋 Description",
            value=description,
            inline=False,
        )

    # --------------------------------------------------------
    # OPTIONAL LINKS
    # --------------------------------------------------------

    if links:

        embed.add_field(
            name="🔗 Links",
            value=links,
            inline=False,
        )

    # --------------------------------------------------------
    # OPTIONAL ATTACHMENT
    # --------------------------------------------------------

    if attachment_url:

        embed.add_field(
            name="📎 Attachment",
            value=attachment_url,
            inline=False,
        )

    # --------------------------------------------------------
    # INITIAL STATUS
    # --------------------------------------------------------

    embed.add_field(
        name="Status",
        value="🟡 Pending Validation",
        inline=False,
    )

    # --------------------------------------------------------
    # SEND SUBMISSION TO SAME CHANNEL
    # --------------------------------------------------------

    submission_message = await interaction.channel.send(
        embed=embed,
        view=SubmissionView(
            submitter_id=interaction.user.id,
            validated=False,
        ),
    )

    # --------------------------------------------------------
    # SAVE DISCORD MESSAGE ID
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        set_discord_message_id(
            db=db,
            submission_id=submission.id,
            message_id=submission_message.id,
        )

    finally:
        db.close()

    # --------------------------------------------------------
    # CONFIRM TO EMPLOYEE
    # --------------------------------------------------------

    await interaction.response.send_message(
        "✅ Work update submitted successfully.",
        ephemeral=True,
    )