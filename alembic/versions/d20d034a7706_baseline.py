"""
Create the initial database schema.

Revision ID: d20d034a7706
Revises:
Create Date: 2026-09-09 20:10:16.850393
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d20d034a7706"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial database schema."""

    op.create_table(
        "submissions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "links",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "attachment_url",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "employee_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "discord_channel_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "discord_message_id",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "is_validated",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "validated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "validator_id",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "validation_note",
            sa.Text(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("discord_message_id"),
    )


def downgrade() -> None:
    """Remove the initial database schema."""

    op.drop_table("submissions")