import dataclasses
from enum import Enum


class SubmissionMessageType(str, Enum):
    """Submission message types."""

    ERROR = "Error"
    INFO = "Info"
    WARNING = "Warning"


class SubmissionStatus(str, Enum):
    """Submission status values."""

    FAILED = "Failed"
    IN_PROGRESS = "In progress"
    SUCCESSFUL = "Successful"


@dataclasses.dataclass
class SubmissionLogEntry:
    """Submission log entry."""

    entry_number: int
    message_type: SubmissionMessageType
    message: str
