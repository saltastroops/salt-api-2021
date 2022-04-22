from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Connection


def get_department(departments_list: list[str], index: int) -> str:
    try:
        return departments_list[index]
    except IndexError:
        return ""


class InstitutionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_institutions(self) -> List[Dict[str, Any]]:
        """
        Returns a list of institutions
        """
        separator = "::::"
        stmt = text(
            """
SELECT P.Partner_Code   AS partner_code,
       I2.Department    AS department,
       I2.Institute_Id  AS institution_id,
       I.InstituteName_Name AS name
FROM Partner P
         JOIN Institute I2 ON P.Partner_Id = I2.Partner_Id
         JOIN InstituteName I ON I2.InstituteName_Id = I.InstituteName_Id
            """
        )
        result = self.connection.execute(stmt, {"separator": separator})
        institutions = [
            {
                "institution_id": row.institution_id,
                "name": row.name,
                "department": row.department,
                "partner_code": row.partner_code,
            }
            for row in result
        ]
        return institutions
