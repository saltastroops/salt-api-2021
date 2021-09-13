import hashlib
import secrets
from typing import cast

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.service.proposal import ProposalCode
from saltapi.service.user import User, UserToUpdate

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
            raise NotFoundError("Unknown username")
        return User(**user)

    def get_by_email(self, email: str) -> User:
        """
        Returns the user with a given email

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
FROM PiptUser PU
         JOIN Investigator I ON (PU.PiptUser_Id = I.PiptUser_Id)
WHERE I.Email = :email
        """
        )
        result = self.connection.execute(stmt, {"email": email})
        user = result.one_or_none()
        if not user:
            raise NotFoundError("Unknown email address")
        return User(**user)

    def is_investigator(self, username: str, proposal_code: ProposalCode) -> bool:
        """
        Check whether a user is an investigator on a proposal.

        If the user or proposal do not exist, it is assumed the user is no investigator.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM ProposalCode PC
         JOIN ProposalInvestigator PI ON PC.ProposalCode_Id = PI.ProposalCode_Id
         JOIN Investigator I on PI.Investigator_Id = I.Investigator_Id
         JOIN PiptUser PU ON I.PiptUser_Id = PU.PiptUser_Id
WHERE PC.Proposal_Code = :proposal_code AND PU.Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )
        return cast(int, result.scalar_one()) > 0

    def is_principal_investigator(
        self, username: str, proposal_code: ProposalCode
    ) -> bool:
        """
        Check whether a user is the Principal Investigator of a proposal.

        If the user or proposal do not exist, it is assumed the user is no Principal
        Investigator.
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
        return cast(int, result.scalar_one()) > 0

    def is_principal_contact(self, username: str, proposal_code: ProposalCode) -> bool:
        """
        Check whether a user is the Principal Contact of a proposal.

        If the user or proposal do not exist, it is assumed the user is no Principal
        Contact.
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

    def is_activating_investigator(
        self, username: str, proposal_code: ProposalCode
    ) -> bool:
        """
        Check whether the user is an investigator who may activate a given proposal.

        The user is such an investigator if they are the Principal Investigator or
        Contact, and activation is allowed for these.

        If the user or proposal do not exist, it is assumed that the user is no
        activating investigator.
        """
        stmt = text(
            """
SELECT PSA.PiPcMayActivate
FROM ProposalSelfActivation PSA
         JOIN ProposalCode PC ON PSA.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code;
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        one_ore_none = result.scalar_one_or_none()
        pi_pc_may_activate = bool(one_ore_none and cast(int, one_ore_none) > 0)

        return pi_pc_may_activate and (
            self.is_principal_investigator(username, proposal_code)
            or self.is_principal_contact(username, proposal_code)
        )

    def is_salt_astronomer(self, username: str) -> bool:
        """
        Check whether the user is a SALT Astronomer.

        If the user does not exist, it is assumed they are no SALT Astronomer.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU
    JOIN Investigator I ON PU.PiptUser_Id = I.PiptUser_Id
    JOIN SaltAstronomers SA ON I.Investigator_Id = SA.Investigator_Id
WHERE PU.Username = :username
        """
        )
        result = self.connection.execute(stmt, {"username": username})
        return cast(int, result.scalar_one()) > 0

    def is_tac_member(self, username: str, proposal_code: ProposalCode) -> bool:
        """
        Check whether the user is member of a TAC from which a proposal requests time.

        If the user or proposal do not exist, it is assumed the user is no TAC member.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU
         JOIN PiptUserTAC PUT ON PU.PiptUser_Id = PUT.PiptUser_Id
         JOIN MultiPartner MP ON PUT.Partner_Id = MP.Partner_Id
         JOIN ProposalCode PC ON MP.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
  AND MP.ReqTimePercent > 0
  AND Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )

        return cast(int, result.scalar_one()) > 0

    def is_tac_chair(self, username: str, proposal_code: ProposalCode) -> bool:
        """
        Check whether the user is chair of a TAC from which a proposal requests time.

        If the user or proposal do not exist, it is assumed the user is no TAC chair.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU
         JOIN PiptUserTAC PUT ON PU.PiptUser_Id = PUT.PiptUser_Id
         JOIN MultiPartner MP ON PUT.Partner_Id = MP.Partner_Id
         JOIN ProposalCode PC ON MP.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
  AND MP.ReqTimePercent > 0
  AND PUT.Chair > 0
  AND Username = :username
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "username": username}
        )

        return cast(int, result.scalar_one()) > 0

    def is_board_member(self, username: str) -> bool:
        """
        Check whether the user is a SALT Board member.

        If the user does not exist, it is assumed they are no Board member.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUserSetting PUS
         JOIN PiptSetting PS ON PUS.PiptSetting_Id = PS.PiptSetting_Id
         JOIN PiptUser PU ON PUS.PiptUser_Id = PU.PiptUser_Id
WHERE PU.Username = :username
  AND PS.PiptSetting_Name = 'RightBoard'
  AND PUS.Value > 0;
        """
        )
        result = self.connection.execute(stmt, {"username": username})

        return cast(int, result.scalar_one()) > 0

    def is_administrator(self, username: str) -> bool:
        """
        Check whether the user is an administrator.

        If the user does not exist, it is assumed they are no administrator.
        """
        stmt = text(
            """
SELECT COUNT(*)
FROM PiptUser PU
    JOIN PiptUserSetting PUS ON PU.PiptUser_Id = PUS.PiptUser_Id
    JOIN PiptSetting PS ON PUS.PiptSetting_Id = PS.PiptSetting_Id
WHERE PS.PiptSetting_Name = 'RightAdmin'
    AND PUS.Value > 1
    AND PU.Username = :username
        """
        )
        result = self.connection.execute(stmt, {"username": username})
        return cast(int, result.scalar()) > 0

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plain text password."""
        return hashlib.md5(password.encode("utf-8")).hexdigest()  # nosec

    def update_password_hash(self, username: str, password: str) -> None:
        new_password_hash = self.get_new_password_hash(password)
        stmt = text(
            """
INSERT INTO Password (Username, Password)
VALUES (:username, :password)
ON DUPLICATE KEY UPDATE Password = :password
        """
        )
        self.connection.execute(
            stmt, {"username": username, "password": new_password_hash}
        )

    def _update_password(self, username: str, password: str):
        self.update_password_hash(username, password)
        password_hash = self.get_password_hash(password)
        stmt = text(
            """
UPDATE PiptUser
SET Password = :password
WHERE Username = :username
        """
        )
        self.connection.execute(
            stmt, {"username": username, "password": password_hash}
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

    def find_user_with_username_and_password(
        self, username: str, password: str
    ) -> User:
        """
        Find a user with a username and password.

        If the combination of username and password is valid, then the corresponding
        user is returned. Otherwise a NotFoundError is raised.
        """
        user = self.get(username)
        if not user:
            raise NotFoundError()
        if not self.verify_password(password, user.password_hash):
            raise NotFoundError()

        return user
