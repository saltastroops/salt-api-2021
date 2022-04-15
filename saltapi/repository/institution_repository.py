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
        separator = "::::"
        stmt = text(
            """
SELECT P.Partner_Name   AS partner,
       I2.Department    AS department,
       GROUP_CONCAT(DISTINCT `IN`.InstituteName_Name ORDER BY `IN`.InstituteName_Name SEPARATOR :separator) AS institutes
FROM Partner P
         JOIN Institute I2 ON P.Partner_Id = I2.Partner_Id
         JOIN InstituteName `IN` ON I2.InstituteName_Id = `IN`.InstituteName_Id
GROUP BY P.Partner_Name
            """
        )
        result = self.connection.execute(stmt, {"separator": separator})
        affiliations = [
            {
                "partner": row.partner,
                "department": row.department,
                "institutes": row.institutes.split(separator),
            }
            for row in result
        ]
        return affiliations
