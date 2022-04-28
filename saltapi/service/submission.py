from enum import Enum


class SubmissionMessageType(Enum):
    """Submission message types."""
    ERROR = "Error"
    INFO = "Info"
    WARNING = "Warning"
