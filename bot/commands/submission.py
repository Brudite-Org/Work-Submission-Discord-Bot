"""
Discord command handlers for employee work submissions.
"""

import logging

from discord import (
    Attachment,
    Color,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    app_commands,
)
from discord.utils import format_dt
from sqlalchemy.exc import SQLAlchemyError

from app.services.submission_service import (
    create_submission,
    set_discord_message_id,
)
from bot.views.submission_view import SubmissionView
from config.database import async_session_factory


logger = logging.getLogger(__name__)


submit_group = app_commands.Group(
    name="submit",
    description="Submit employee work updates",
)


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
    interaction: Interaction,
    title: app_commands.Range[str, 1, 255],
    description: app_commands.Range[str, 1, 1024] | None = None,
    links: app_commands.Range[str, 1, 1024] | None = None,
    attachment: Attachment | None = None,
) -> None:
    """Create and publish an employee work submission."""

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

    attachment_url = attachment.url if attachment else None

    try:
        async with async_session_factory() as db:
            submission = await create_submission(
                db=db,
                title=title,
                description=description,
                links=links,
                attachment_url=attachment_url,
                employee_id=interaction.user.id,
                channel_id=channel.id,
            )

    except SQLAlchemyError:
        logger.exception(
            "Database error while creating submission.",
        )

        await interaction.followup.send(
            "❌ A database error occurred while saving "
            "your submission. Please try again.",
            ephemeral=True,
        )
        return

    except Exception:
        logger.exception(
            "Unexpected error while creating submission.",
        )

        await interaction.followup.send(
            "❌ An unexpected error occurred. Please try again later.",
            ephemeral=True,
        )
        return

    embed = Embed(
        title="📝 WORK UPDATE",
        color=Color.orange(),
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
        value=format_dt(
            submission.submitted_at,
            style="F",
        ),
        inline=False,
    )

    if description:
        embed.add_field(
            name="📋 Description",
            value=description,
            inline=False,
        )

    if links:
        embed.add_field(
            name="🔗 Links",
            value=links,
            inline=False,
        )

    if attachment_url:
        embed.add_field(
            name="📎 Attachment",
            value=attachment_url,
            inline=False,
        )

    embed.add_field(
        name="Status",
        value="🟡 Pending Validation",
        inline=False,
    )

    try:
        submission_message = await channel.send(
            embed=embed,
            view=SubmissionView(),
        )

    except Forbidden:
        logger.exception(
            "Discord permission error while posting submission.",
        )

        await interaction.followup.send(
            "❌ I don't have permission to post "
            "the submission in this channel.",
            ephemeral=True,
        )
        return

    except HTTPException:
        logger.exception(
            "Discord HTTP error while posting submission.",
        )

        await interaction.followup.send(
            "❌ Discord could not post your submission. "
            "Please try again.",
            ephemeral=True,
        )
        return

    except Exception:
        logger.exception(
            "Unexpected error while posting submission to Discord.",
        )

        await interaction.followup.send(
            "❌ An unexpected error occurred. Please try again later.",
            ephemeral=True,
        )
        return

    try:
        async with async_session_factory() as db:
            await set_discord_message_id(
                db=db,
                submission_id=submission.id,
                message_id=submission_message.id,
            )

    except SQLAlchemyError:
        logger.exception(
            "Database error while saving Discord message ID.",
        )

        try:
            await submission_message.delete()
        except HTTPException:
            logger.exception(
                "Failed to delete Discord message after database error.",
            )
        except Exception:
            logger.exception(
                "Unexpected error while deleting Discord message.",
            )

        await interaction.followup.send(
            "❌ The submission was posted to Discord, "
            "but it could not be saved correctly. "
            "Please try again.",
            ephemeral=True,
        )
        return

    except Exception:
        logger.exception(
            "Unexpected error while saving the Discord message ID.",
        )

        try:
            await submission_message.delete()
        except HTTPException:
            logger.exception(
                "Failed to delete Discord message after unexpected error.",
            )
        except Exception:
            logger.exception(
                "Unexpected error while deleting Discord message.",
            )

        await interaction.followup.send(
            "❌ An unexpected error occurred. Please try again later.",
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        "✅ Work update submitted successfully.",
        ephemeral=True,
    )