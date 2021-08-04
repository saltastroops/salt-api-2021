import hashlib
import secrets
from typing import cast, Optional

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.engine import Connection
from passlib.context import CryptContext

from saltapi.exceptions import NotFoundError
from saltapi.service.user import User


pwd_context = CryptContext(
    schemes=["bcrypt", "md5_crypt"], default="bcrypt", deprecated="auto"
)

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

    def is_salt_astronomer(self, username: str) -> bool:
        """
        Check whether a user is the Principal Contact of a proposal.

        If the user does not exist, it is assumed they are no Principal Contact.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU 
    JOIN SaltAstronomers SA ON SA.Investigator_Id = PU.Investigator_Id
WHERE PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"username": username}
        )
        return cast(int, result.scalar()) > 0

    def is_administrator(self, username: str) -> bool:
        """
        Check whether a user is the Principal Contact of a proposal.

        If the user does not exist, it is assumed they are no Principal Contact.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU 
    JOIN PiptUserSetting PUS ON PU.PiptUser_Id = PUS.PiptUser_Id
WHERE PUS.PiptSetting_Id = 22 AND PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"username": username}
        )
        return cast(int, result.scalar()) > 0

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plain text password."""
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    def update_password_hash(self, username: str, password: str) -> None:
        new_password_hash = self.get_new_password_hash(password)
        stmt = text(
            """
INSERT INTO Password(Username, Password)
VALUES (:username, :password)
ON DUPLICATE KEY UPDATE Username= :username
        """
        )
        self.connection.execute(
            stmt, { "username": username, "password": new_password_hash}
        )

    @staticmethod
    def get_new_password_hash(password: str) -> str:
        """Hash a plain text password."""

        # Note that the type hint for the return value of the hash method is Any,
        # but the method is guaranteed to return a str.
        return cast(str, pwd_context.hash(password))

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Check a plain text password against a hash."""
        password_hash = self.get_password_hash(password)
        return secrets.compare_digest(password_hash, hashed_password)

    def find_user_with_username_and_password(self, username, password) -> Optional[User]:
        """
        Find a user with a username and password.

        If the combination of username and password are valid, then corresponding
        user is returned. Otherwise None is returned.
        """
        user = self.get(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None

        return user
