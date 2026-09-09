from sqlalchemy import select
from sqlalchemy.orm import Session

from models.submission import Submission
from models.submission_validation import SubmissionValidation


def create_submission(
    db: Session,
    title: str,
    description: str | None,
    links: str | None,
    attachment_url: str | None,
    employee_id: int,
    channel_id: int,
) -> Submission:
    submission = Submission(
        title=title,
        description=description,
        links=links,
        attachment_url=attachment_url,
        employee_id=employee_id,
        discord_channel_id=channel_id,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission


def set_discord_message_id(
    db: Session,
    submission_id: int,
    message_id: int,
) -> Submission:
    submission = db.get(
        Submission,
        submission_id,
    )

    if submission is None:
        raise ValueError(
            "Submission not found"
        )

    submission.discord_message_id = message_id

    db.commit()
    db.refresh(submission)

    return submission


def get_submission_by_message_id(
    db: Session,
    message_id: int,
) -> Submission:
    statement = select(Submission).where(
        Submission.discord_message_id == message_id
    )

    submission = db.scalar(statement)

    if submission is None:
        raise ValueError(
            "Submission not found"
        )

    return submission


def get_submission_validations(
    db: Session,
    submission_id: int,
) -> list[SubmissionValidation]:
    submission = db.get(
        Submission,
        submission_id,
    )

    if submission is None:
        raise ValueError(
            "Submission not found"
        )

    return submission.validations


def validate_submission(
    db: Session,
    submission_id: int,
    validator_id: int,
    validation_note: str | None,
) -> Submission:
    submission = db.get(
        Submission,
        submission_id,
    )

    if submission is None:
        raise ValueError(
            "Submission not found"
        )

    if submission.employee_id == validator_id:
        raise ValueError(
            "You cannot validate your own submission"
        )

    statement = select(
        SubmissionValidation
    ).where(
        SubmissionValidation.submission_id == submission_id,
        SubmissionValidation.validator_id == validator_id,
    )

    existing_validation = db.scalar(
        statement
    )

    if existing_validation is not None:
        raise ValueError(
            "You have already validated this submission"
        )

    validation = SubmissionValidation(
        submission_id=submission_id,
        validator_id=validator_id,
        validation_note=validation_note,
    )

    db.add(validation)

    submission.is_validated = True

    db.commit()
    db.refresh(submission)

    return submission