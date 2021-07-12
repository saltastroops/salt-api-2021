from typing import cast

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.service.user import User


class UserRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, username: str) -> User:
        """
        Returns the user with a given username.

        If the username does not exist, a NotFoundError is raised.
        """
        stmt = text(
            """
SELECT PU.PiptUser_Id  AS id,
       Email           AS email,
       Surname         AS family_name,
       FirstName       AS given_name,
       Password        AS password_hash,
       Username        AS username
FROM PiptUser AS PU
         JOIN Investigator AS I ON (PU.Investigator_Id = I.Investigator_Id)
WHERE PU.Username = :username
        """
        )
        result = self.connection.execute(stmt, {"username": username})
        user = result.one_or_none()
        if not user:
            raise NotFoundError("Unknown user id")
        return User(**user)

    def is_investigator(self, username: str, proposal_code: str) -> bool:
        """
        Check whether a user is an investigator on a proposal.

        If the user does not exist, it is assumed they are no investigator.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM ProposalCode PC
         JOIN ProposalInvestigator PI ON PC.ProposalCode_Id = PI.ProposalCode_Id
         JOIN Investigator I on PI.Investigator_Id = I.Investigator_Id
         JOIN PiptUser PU ON I.Investigator_Id = PU.Investigator_Id
WHERE PC.Proposal_Code = :proposal_code AND PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )
        return cast(int, result.scalar()) > 0

    def is_principal_investigator(self, username: str, proposal_code: str) -> bool:
        """
        Check whether a user is the Principal Investigator of a proposal.

        If the user does not exist, it is assumed they are no Principal Investigator.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM ProposalCode PCode
         JOIN ProposalContact PContact
                   ON PCode.ProposalCode_Id = PContact.ProposalCode_Id
         JOIN Investigator I ON PContact.Leader_Id = I.Investigator_Id
         JOIN PiptUser PU ON I.PiptUser_Id = PU.PiptUser_Id
WHERE PCode.Proposal_Code = :proposal_code AND PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )
        return cast(int, result.scalar()) > 0

    def is_principal_contact(self, username: str, proposal_code: str) -> bool:
        """
        Check whether a user is the Principal Contact of a proposal.

        If the user does not exist, it is assumed they are no Principal Contact.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM ProposalCode PCode
         JOIN ProposalContact PContact
                    ON PCode.ProposalCode_Id = PContact.ProposalCode_Id
         JOIN Investigator I ON PContact.Contact_Id = I.Investigator_Id
         JOIN PiptUser PU ON I.PiptUser_Id = PU.PiptUser_Id
WHERE PCode.Proposal_Code = :proposal_code AND PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )
        return cast(int, result.scalar()) > 0
