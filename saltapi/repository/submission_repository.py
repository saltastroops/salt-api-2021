import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError
from saltapi.service.submission import SubmissionMessageType, SubmissionStatus
from saltapi.service.user import User


class SubmissionRepository:
    def __init__(self, connection: Connection):
        """
        Create a submission repository instance.

        WARNING: AUTOCOMMIT is enabled on the database connection.

        Parameters
        ----------
        connection: Connection
            Database connection. WARNING: AUTOCOMMIT will be enabled on this connection.
        """
        self.connection = connection.execution_options(isolation_level="AUTOCOMMIT")

    def get(self, identifier: str) -> Dict[str, Any]:
        """
        Get the submission details.

        Parameters
        ----------
        identifier: str
            The submission identifier.

        Returns
        -------
        dict
            The submission details.
        """
        stmt = text(
            """
SELECT PC.Proposal_Code    AS proposal_code,
       S.Submitter_Id      AS submitter_id,
       SS.SubmissionStatus AS status,
       S.StartedAt         AS started_at,
       S.FinishedAt        AS finished_at
FROM Submission S
         LEFT JOIN ProposalCode PC ON S.ProposalCode_Id = PC.ProposalCode_Id
         JOIN SubmissionStatus SS ON S.SubmissionStatus_Id = SS.SubmissionStatus_Id
WHERE S.Identifier = :identifier
        """
        )
        result = self.connection.execute(stmt, {"identifier": identifier})
        try:
            row = result.one()
            normalized_status = row.status[:1].upper() + row.status[1:].lower()
            return {
                "proposal_code": row.proposal_code,
                "submitter_id": row.submitter_id,
                "status": SubmissionStatus(normalized_status),
                "started_at": pytz.utc.localize(row.started_at),
                "finished_at": pytz.utc.localize(row.finished_at)
                if row.finished_at
                else None,
            }
        except NoResultFound:
            raise NotFoundError()

    def create(self, user: User, proposal_code: Optional[str]) -> str:
        """
        Create a new submission in the database.

        Returns
        -------
        str
            The identifier for the created submission.
        """
        identifier = str(uuid.uuid4())
        proposal_code_id = (
            self._proposal_code_id(proposal_code) if proposal_code else None
        )
        stmt = text(
            """
INSERT INTO Submission (Identifier, Submitter_Id, ProposalCode_Id, SubmissionStatus_Id,
                        StartedAt)
    VALUES (
        :identifier,
        :user_id,
        :proposal_code_id,
        (SELECT SubmissionStatus_Id FROM SubmissionStatus
         WHERE SubmissionStatus='In Progress'),
        :started_at
    )
            """
        )
        self.connection.execute(
            stmt,
            {
                "identifier": identifier,
                "user_id": user.id,
                "proposal_code_id": proposal_code_id,
                # We use a naive datetime for the start time, as the time should be
                # stored as UTC, but the database might use another timezone.
                "started_at": datetime.utcnow(),
            },
        )

        return identifier

    def finish(self, identifier: str, status: SubmissionStatus) -> None:
        """
        Set the final status of a submission and the finishing time.

        Parameters
        ----------
        identifier: str
            The submission identifier.
        status: SubmissionStatus
            The final submission status.
        """

        # We use a naive datetime for the finish time as the time should be stored as
        # UTC, but the database might use another timezone.
        now = datetime.utcnow()

        status_value = (
            status.value if status != SubmissionStatus.IN_PROGRESS else "In progress"
        )

        # Make sure the submission exists
        submission_id = self._submission_id(identifier)

        stmt = text(
            """
UPDATE Submission
SET SubmissionStatus_Id=(SELECT SubmissionStatus_Id
                         FROM SubmissionStatus
                         WHERE SubmissionStatus = :status),
    FinishedAt         = :finished_at
WHERE Submission_Id = :submission_id
        """
        )
        self.connection.execute(
            stmt,
            {
                "submission_id": submission_id,
                "status": status_value,
                "finished_at": now,
            },
        )

    def _submission_id(self, identifier: str) -> str:
        stmt = text(
            """
SELECT Submission_Id AS submission_id FROM Submission S WHERE S.Identifier = :identifier
        """
        )
        result = self.connection.execute(stmt, {"identifier": identifier})
        try:
            return str(result.scalar_one())
        except NoResultFound:
            raise NotFoundError(
                f"The submission identifier {identifier} does not exist."
            )

    def _proposal_code_id(self, proposal_code: str) -> str:
        stmt = text(
            """
SELECT ProposalCode_Id
FROM ProposalCode
WHERE Proposal_Code = :proposal_code
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        try:
            proposal_code_id = result.scalar_one()
            return str(proposal_code_id)
        except NoResultFound:
            raise NotFoundError(f"The proposal code {proposal_code} does not exist.")

    def get_log_entries(
        self, identifier: str, from_entry_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get the log entries for a submission.

        If a ``from_entry_number`` is specified, only log entries with an entry number
        greater than or equal to this value are returned.

        Parameters
        ----------
        identifier: str
            The submission identifier.
        from_entry_number:
            The first entry number to include.

        Returns
        -------
        list of dict
            The submission log entries, ordered by log entry number in ascending order.
        """
        stmt = text(
            """
SELECT SLE.SubmissionLogEntryNumber AS entry_number,
       SMT.SubmissionMessageType    AS message_type,
       SLE.Message                  AS message,
       SLE.LoggedAt                 AS logged_at
FROM SubmissionLogEntry AS SLE
         JOIN Submission S ON SLE.Submission_Id = S.Submission_Id
         JOIN SubmissionMessageType SMT
              ON SLE.SubmissionMessageType_Id = SMT.SubmissionMessageType_Id
WHERE S.Identifier = :identifier AND  SLE.SubmissionLogEntryNumber >= :from_entry_number
ORDER BY entry_number;
        """
        )
        result = self.connection.execute(
            stmt, {"identifier": identifier, "from_entry_number": from_entry_number}
        )
        return [
            {
                "entry_number": row.entry_number,
                "message_type": SubmissionMessageType(row.message_type),
                "message": row.message,
                "logged_at": pytz.utc.localize(row.logged_at),
            }
            for row in result
        ]

    def get_progress(
        self, identifier: str, from_entry_number: int = 1
    ) -> Dict[str, Any]:
        """
        Return the status and log entries for a submission.

        You can limit the returned log entries to those with an entry number greater
        than or equal to a given value with the `from_entry_number` argument.

        Parameters
        ----------
        from_entry_number: int
            Entry number from which onwards to return the log entries.

        Returns
        -------
        dict
            A dictionary of the status and list of log entries.
        """
        progress = self.get(identifier)
        return {
            "status": progress["status"],
            "log_entries": self.get_log_entries(identifier, from_entry_number),
            "proposal_code": progress["proposal_code"],
        }

    def create_log_entry(
        self,
        submission_identifier: str,
        message_type: SubmissionMessageType,
        message: str,
    ) -> None:
        """
        Create a log entry.

        Parameters
        ----------
        submission_identifier: str
            The identifier of the submission for which the log entry is created.
        message_type: SubmissionMessageType
            The log message type.
        message: str
            The log message text.
        """

        submission_id = self._submission_id(submission_identifier)

        now = pytz.utc.localize(datetime.utcnow())
        stmt = text(
            """
INSERT INTO SubmissionLogEntry
(Submission_Id, SubmissionLogEntryNumber, SubmissionMessageType_Id, Message, LoggedAt)
VALUES (:submission_id,
        (
            SELECT COUNT(*) + 1
            FROM SubmissionLogEntry SLE
            WHERE SLE.Submission_Id = :submission_id
        ),
        (
            SELECT SMT.SubmissionMessageType_Id
            FROM SubmissionMessageType AS SMT
            WHERE SMT.SubmissionMessageType = :message_type
        ),
        :message,
        :now)
        """
        )
        self.connection.execute(
            stmt,
            {
                "submission_id": submission_id,
                "message_type": message_type.value,
                "message": message,
                "now": now,
            },
        )
