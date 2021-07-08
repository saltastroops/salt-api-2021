from typing import List

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.proposal import ContactDetails, ProposalSummary


class ProposalRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def _list(self) -> List[ProposalSummary]:
        stmt = text(
            """
SELECT P.Proposal_Id                   AS id,
       PC.Proposal_Code                AS proposal_code,
       CONCAT(S.Year, '-', S.Semester) AS semester,
       PT.Title                        AS title,
       P.Phase                         AS phase,
       PS.Status                       AS status,
       T.ProposalType                  AS proposal_type,
       Leader.FirstName                AS pi_given_name,
       Leader.Surname                  AS pi_family_name,
       Leader.Email                    AS pi_email,
       Contact.FirstName               AS pc_given_name,
       Contact.Surname                 AS pc_family_name,
       Contact.Email                   AS pc_email,
       Astronomer.FirstName            AS la_given_name,
       Astronomer.Surname              AS la_family_name,
       Astronomer.Email                AS la_email
FROM Proposal P
         JOIN ProposalCode PC on P.ProposalCode_Id = PC.ProposalCode_Id
         JOIN ProposalGeneralInfo PGI on PC.ProposalCode_Id = PGI.ProposalCode_Id
         JOIN ProposalText PT ON PC.ProposalCode_Id = PT.ProposalCode_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         JOIN ProposalStatus PS on PGI.ProposalStatus_Id = PS.ProposalStatus_Id
         JOIN ProposalType T on PGI.ProposalType_Id = T.ProposalType_Id
         JOIN ProposalContact C on PC.ProposalCode_Id = C.ProposalCode_Id
         JOIN Investigator Astronomer on C.Astronomer_Id = Astronomer.Investigator_Id
         JOIN Investigator Contact ON C.Contact_Id = Contact.Investigator_Id
         JOIN Investigator Leader ON C.Leader_Id = Leader.Investigator_Id
WHERE P.Current = 1
LIMIT 2
        """
        )
        result = self.connection.execute(stmt)

        return [
            ProposalSummary(
                id=row.id,
                proposal_code=row.proposal_code,
                semester=row.semester,
                title=row.title,
                phase=row.phase,
                status=row.status,
                proposal_type=row.proposal_type,
                principal_investigator=ContactDetails(
                    given_name=row["pi_given_name"],
                    family_name=row["pi_family_name"],
                    email=row["pi_email"],
                ),
                principal_contact=ContactDetails(
                    given_name=row["pc_given_name"],
                    family_name=row["pc_family_name"],
                    email=row["pc_email"],
                ),
                liaison_astronomer=ContactDetails(
                    given_name=row["la_given_name"],
                    family_name=row["la_family_name"],
                    email=row["la_email"],
                ),
            )
            for row in result
        ]

    def list(self) -> List[ProposalSummary]:
        return self._list()
