"""
Replace single-validator submission fields with validation records.

Revision ID: c11a7e1e2ab7
Revises: d20d034a7706
Create Date: 2026-09-09 20:12:29.868832
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "c11a7e1e2ab7"
down_revision: str | None = "d20d034a7706"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace old validation columns with validation records."""

    op.drop_column(
        "submissions",
        "validated_at",
    )

    op.drop_column(
        "submissions",
        "validator_id",
    )

    op.drop_column(
        "submissions",
        "validation_note",
    )

    op.create_table(
        "submission_validations",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "submission_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "validator_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "validation_note",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "validated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submissions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "submission_id",
            "validator_id",
            name="uq_submission_validator",
        ),
    )


def downgrade() -> None:
    """Restore the previous single-validator validation fields."""

    op.drop_table(
        "submission_validations",
    )

    op.add_column(
        "submissions",
        sa.Column(
            "validation_note",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "submissions",
        sa.Column(
            "validator_id",
            sa.BigInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "submissions",
        sa.Column(
            "validated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )