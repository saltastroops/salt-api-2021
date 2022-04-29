from enum import Enum


class SubmissionMessageType(Enum):
    """Submission message types."""

    ERROR = "Error"
    INFO = "Info"
    WARNING = "Warning"


class SubmissionStatus(Enum):
    """Submission status values."""

    FAILED = "Failed"
    IN_PROGRESS = "In progress"
    SUCCESSFUL = "Successful"
