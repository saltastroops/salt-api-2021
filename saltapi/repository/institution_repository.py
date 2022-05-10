from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Connection


class InstitutionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_institutions(self) -> List[Dict[str, Any]]:
        """
        Returns a list of institutions
        """
        stmt = text(
            """
SELECT 
    P.Partner_Code   AS partner_code,
    P.Partner_Name   AS partner_name,
    I2.Department    AS department,
    I2.Institute_Id  AS institution_id,
    I.InstituteName_Name AS institution
FROM Partner P
    JOIN Institute I2 ON P.Partner_Id = I2.Partner_Id
    JOIN InstituteName I ON I2.InstituteName_Id = I.InstituteName_Id
            """
        )
        result = self.connection.execute(stmt)
        institutions = [
            {
                "institution_id": row.institution_id,
                "institution": row.institution,
                "department": row.department,
                "partner_code": row.partner_code,
                "partner_name": row.partner_name,
            }
            for row in result
        ]
        return institutions
