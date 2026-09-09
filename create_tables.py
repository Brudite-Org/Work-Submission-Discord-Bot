from config.database import engine

from models.base import Base
from models.submission import Submission
from models.submission_validation import SubmissionValidation


Base.metadata.create_all(engine)

print("Tables created.")