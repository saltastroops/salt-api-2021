import uuid

from sqlalchemy import text
from sqlalchemy.engine import Connection


class SubmissionRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def create_submission(self) -> str:
        """
        Create a new submission in the database.

        Returns
        -------
        str
            The identifier for the created submission.
        """
        identifier = str(uuid.uuid4())
        stmt = text(
            """
INSERT INTO Submission (Identifier, Submitter_Id, ProposalCode_Id, SubmissionStatus_Id,
                        StartedAt)
    VALUES (
        :identifier,
        (SELECT PiptUser_Id FROM PiptUser WHERE Username = :username),
        IF(
           ISNULL(:proposal_code),
           NULL,
           (
               SELECT ProposalCode_Id
               FROM ProposalCode
               WHERE Proposal_Code = :proposal_code
           )
        ),
        (SELECT SubmissionStatus_Id FROM SubmissionStatus
         WHERE SubmissionStatus='In Progress'),
        NOW()
    )
            """
        )
        result = self.connection.execute(stmt, {"identifier": identifier})
