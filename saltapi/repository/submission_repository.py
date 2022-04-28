import uuid
from typing import Any, Dict, List, Optional

import pytz
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError, ValidationError
from saltapi.service.submission import SubmissionMessageType
from saltapi.service.user import User


class SubmissionRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

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
            return {
                "proposal_code": row.proposal_code,
                "submitter_id": row.submitter_id,
                "status": row.status[:1].upper() + row.status[1:].lower(),
                "started_at": pytz.utc.localize(row.started_at),
                "finished_at": pytz.utc.localize(row.finished_at)
                if row.finished_at
                else None,
            }
        except NoResultFound:
            raise NotFoundError()

    def create_submission(self, user: User, proposal_code: Optional[str]) -> str:
        """
        Create a new submission in the database.

        Returns
        -------
        str
            The identifier for the created submission.
        """
        identifier = str(uuid.uuid4())
        proposal_code_id = self._proposal_code_id(proposal_code) if proposal_code else None
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
        NOW()
    )
            """
        )
        self.connection.execute(
            stmt,
            {
                "identifier": identifier,
                "user_id": user.id,
                "proposal_code_id": proposal_code_id,
            },
        )

        return identifier

    def  _proposal_code_id(self, proposal_code: str) -> str:
        stmt = text("""
SELECT ProposalCode_Id
FROM ProposalCode
WHERE Proposal_Code = :proposal_code
        """)
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        try:
            proposal_code_id = result.scalar_one()
            return str(proposal_code_id)
        except NoResultFound:
            raise ValidationError(f"The proposal code {proposal_code} does not exist.")

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
                "message_type": row.message_type,
                "message": row.message,
                "logged_at": pytz.utc.localize(row.logged_at),
            }
            for row in result
        ]

    def create_log_entry(self, submission_identifier: str,  message_type: SubmissionMessageType, message: str) -> None:
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

        stmt = text("""
INSERT INTO SubmissionLogEntry
(Submission_Id, SubmissionLogEntryNumber, SubmissionMessageType_Id, Message)
VALUES ((SELECT S.Submission_Id FROM Submission AS S WHERE S.Identifier = :identifier),
        (
            SELECT COUNT(*) + 1
            FROM SubmissionLogEntry SLE
                     JOIN Submission S2 ON SLE.Submission_Id = S2.Submission_Id
            WHERE S2.Identifier = :identifier
        ),
        (
            SELECT SMT.SubmissionMessageType_Id
            FROM SubmissionMessageType AS SMT
            WHERE SMT.SubmissionMessageType = :message_type
        ),
        :message)
        """)
        self.connection.execute(stmt, {"identifier": submission_identifier, "message_type": message_type.value, "message": message})

