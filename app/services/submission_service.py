"""
Database operations for employee work submissions.
"""

from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from models.submission import Submission
from models.submission_validation import SubmissionValidation


async def create_submission(
    db: AsyncSession,
    title: str,
    description: str | None,
    links: str | None,
    attachment_url: str | None,
    employee_id: int,
    channel_id: int,
) -> Submission:
    """Create and persist a new employee work submission."""

    submission = Submission(
        title=title,
        description=description,
        links=links,
        attachment_url=attachment_url,
        employee_id=employee_id,
        discord_channel_id=channel_id,
    )

    db.add(submission)

    try:
        await db.commit()
        await db.refresh(submission)

    except SQLAlchemyError:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise

    return submission


async def set_discord_message_id(
    db: AsyncSession,
    submission_id: int,
    message_id: int,
) -> Submission:
    """Associate a Discord message with an existing submission."""

    submission = await db.get(
        Submission,
        submission_id,
    )

    if submission is None:
        raise ValueError("Submission not found")

    submission.discord_message_id = message_id

    try:
        await db.commit()
        await db.refresh(submission)

    except SQLAlchemyError:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise

    return submission


async def get_submission_by_message_id(
    db: AsyncSession,
    message_id: int,
) -> Submission:
    """Retrieve a submission using its Discord message ID."""

    statement = select(Submission).where(
        Submission.discord_message_id == message_id,
    )

    submission = await db.scalar(statement)

    if submission is None:
        raise ValueError("Submission not found")

    return submission


async def get_submission_validations(
    db: AsyncSession,
    submission_id: int,
) -> list[SubmissionValidation]:
    """Retrieve all validations for a submission chronologically."""

    statement = (
        select(SubmissionValidation)
        .where(
            SubmissionValidation.submission_id == submission_id,
        )
        .order_by(
            SubmissionValidation.validated_at,
        )
    )

    result = await db.scalars(statement)

    return list(result)


async def validate_submission(
    db: AsyncSession,
    submission_id: int,
    validator_id: int,
    validation_note: str | None,
) -> Submission:
    """Validate a submission on behalf of an eligible validator."""

    submission = await db.get(
        Submission,
        submission_id,
    )

    if submission is None:
        raise ValueError("Submission not found")

    if submission.employee_id == validator_id:
        raise ValueError(
            "You cannot validate your own submission",
        )

    statement = select(SubmissionValidation).where(
        SubmissionValidation.submission_id == submission_id,
        SubmissionValidation.validator_id == validator_id,
    )

    existing_validation = await db.scalar(statement)

    if existing_validation is not None:
        raise ValueError(
            "You have already validated this submission",
        )

    validation = SubmissionValidation(
        submission_id=submission_id,
        validator_id=validator_id,
        validation_note=validation_note,
    )

    db.add(validation)
    submission.is_validated = True

    try:
        await db.commit()
        await db.refresh(submission)

    except IntegrityError as error:
        await db.rollback()

        raise ValueError(
            "You have already validated this submission",
        ) from error

    except SQLAlchemyError:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise

    return submission