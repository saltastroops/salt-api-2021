from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.user import User


class UserRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, user_id: int) -> User:
        stmt = text("""        
SELECT PU.PiptUser_Id  AS id,
       Email           AS email,
       Surname         AS family_name,
       FirstName       AS given_name,
       Password        AS password_hash,
       Username        AS username
FROM PiptUser AS PU
         JOIN Investigator AS I ON (PU.Investigator_Id = I.Investigator_Id)
WHERE PU.PiptUser_Id = :id
        """)
        result = self.connection.execute(stmt, {"id": user_id})
        user = result.one_or_none()
        if not user:
            raise ValueError("Unknown user id")
        return User(**user)
