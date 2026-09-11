from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

#only impoort this when tools such as type checkers need it to avoid circular dependencies
if TYPE_CHECKING:
    from models.submission_validation import SubmissionValidation


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    links: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attachment_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    discord_channel_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    discord_message_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        unique=True,
    )

    is_validated: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )




    validations: Mapped[list["SubmissionValidation"]] = relationship(
        back_populates="submission",
    )