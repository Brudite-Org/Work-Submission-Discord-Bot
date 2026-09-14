"""
SQLAlchemy model representing a validator's validation of a submission.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base


if TYPE_CHECKING:
    from models.submission import Submission


class SubmissionValidation(Base):
    """Represent one validator's validation of an employee submission."""

    __tablename__ = "submission_validations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=False,
    )

    validator_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    validation_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    submission: Mapped["Submission"] = relationship(
        back_populates="validations",
    )

    __table_args__ = (
        UniqueConstraint(
            "submission_id",
            "validator_id",
            name="uq_submission_validator",
        ),
    )
