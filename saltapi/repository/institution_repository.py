from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.web.schema.institution import Partner


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

        #  Increase the limit on the number of characters from the resultant query
        stmt0 = text(
            """
SET session group_concat_max_len=15000
            """
        )
        self.connection.execute(stmt0)

        stmt = text(
            """
SELECT P.Partner_Code   AS partner_code,
       GROUP_CONCAT(DISTINCT I2.Department ORDER BY I.InstituteName_Name SEPARATOR :separator) AS departments,
       GROUP_CONCAT(DISTINCT I2.Institute_Id ORDER BY I.InstituteName_Name SEPARATOR :separator) AS institute_ids,
       GROUP_CONCAT(DISTINCT I.InstituteName_Name ORDER BY I.InstituteName_Name SEPARATOR :separator) AS institutes
FROM Partner P
         JOIN Institute I2 ON P.Partner_Id = I2.Partner_Id
         JOIN InstituteName I ON I2.InstituteName_Id = I.InstituteName_Id
GROUP BY P.Partner_Code
            """
        )
        result = self.connection.execute(stmt, {"separator": separator})
        institutions = [
            {
                "partner": Partner[row.partner_code].value,
                "institutes": [
                    {
                        "institute_id": row.institute_ids.split(separator)[i],
                        "name": row.institutes.split(separator)[i],
                        "department": get_department(
                            row.departments.split(separator), i
                        ),
                    }
                    for i in range(len(row.institutes.split(separator)))
                ],
            }
            for row in result
        ]
        return institutions
