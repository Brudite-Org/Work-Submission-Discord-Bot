import discord
from discord import app_commands

from app.services.submission_service import (
    create_submission,
    set_discord_message_id,
)
from bot.views.submission_view import SubmissionView
from config.database import SessionLocal



#this is the group of our submit command 
submit_group = app_commands.Group(
    name="submit",
    description="Submit employee work updates",
)



#we are creating an /submit work in submit group
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

    #we are getting the attachment url to store in db and give response
    attachment_url = None

    if attachment is not None:
        attachment_url = attachment.url


    #abhi database me stowre kr rhe h
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

    submission_message = await interaction.channel.send(
        embed=embed,
        view=SubmissionView(
            submitter_id=interaction.user.id,
            validated=False,
        ),
    )


    db = SessionLocal()

    try:

        set_discord_message_id(
            db=db,
            submission_id=submission.id,
            message_id=submission_message.id,
        )

    finally:
        db.close()

 
    await interaction.response.send_message(
        "✅ Work update submitted successfully.",
        ephemeral=True,
    )