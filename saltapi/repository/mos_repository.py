from typing import Any, Optional, Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Connection


class MosRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, semesters: List[str]) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT DISTINCT
    P.Proposal_Id       AS proposal_id,
    Proposal_Code       AS proposal_code,
    PC.ProposalCode_Id  AS proposal_code_id,
    PI.Surname          AS pi_surname,
    BlockStatus         AS block_status,
    Block_Name          AS block_name,
    Priority            AS priority,
    NVisits             AS n_visits,
    NDone               AS n_done,
    Barcode             AS barcode,
    15.0 * RaH + 15.0 * RaM / 60.0 + 15.0 * RaS / 3600.0 AS ra_center,
    CutBy               AS cut_by,
    CutDate             AS cut_date,
    SaComment           AS mask_comment
FROM Proposal P 
    JOIN ProposalCode PC ON (P.ProposalCode_Id=PC.ProposalCode_Id)
    JOIN Semester S ON (P.Semester_Id=S.Semester_Id)
    JOIN ProposalGeneralInfo PGI ON (P.ProposalCode_Id=PGI.ProposalCode_Id)
    JOIN ProposalStatus PS ON (PGI.ProposalStatus_Id=PS.ProposalStatus_Id)
    JOIN ProposalContact PCO ON (P.ProposalCode_Id=PCO.ProposalCode_Id)
    JOIN Investigator PI ON (PCO.Leader_Id=PI.Investigator_Id)
    JOIN Block B ON (P.Proposal_Id=B.Proposal_Id)
    JOIN BlockStatus BS ON (B.BlockStatus_Id=BS.BlockStatus_Id)
    JOIN Pointing PO USING (Block_Id)
    JOIN TelescopeConfigObsConfig USING (Pointing_Id)
    JOIN ObsConfig ON (PlannedObsConfig_Id=ObsConfig_Id)
    JOIN RssPatternDetail USING (RssPattern_Id)
    JOIN Rss using (Rss_Id)
    JOIN RssConfig USING (RssConfig_Id)
    JOIN RssMask RM USING (RssMask_Id)
    JOIN RssMaskType RMT ON (RM.RssMaskType_Id=RMT.RssMaskType_Id)
    JOIN RssMosMaskDetails USING (RssMask_Id)
    JOIN Observation O ON (PO.Pointing_Id=O.Pointing_Id)
    JOIN Target USING (Target_Id)
    JOIN TargetCoordinates USING (TargetCoordinates_Id)
WHERE RssMaskType='MOS' AND O.Observation_Order=1 
    AND CONCAT(S.Year, "-", S.Semester) IN :semesters
ORDER BY P.Semester_Id, Proposal_Code, Proposal_Id DESC
        """
        )
        results = self.connection.execute(stmt, {"semesters": tuple(semesters)})

        proposal_code_ids = []
        mask_data = []
        for row in results:
            mask_data.append(dict(row))
            proposal_code_ids.append(row.proposal_code_id)

        stmt = text("""
SELECT DISTINCT 
    ProposalCode_Id AS proposal_code_id, 
    Surname         AS surname
FROM Proposal
    JOIN ProposalContact PCO USING (ProposalCode_Id)
    JOIN Investigator I ON (PCO.Astronomer_Id=I.Investigator_Id)
WHERE ProposalCode_Id IN :proposal_code_ids
        """)
        results = self.connection.execute(stmt, {"proposal_code_ids": tuple(proposal_code_ids)})
        liaison_astronomers = dict()
        for row in results:
            liaison_astronomers[row["proposal_code_id"]] = row["surname"]

        mask = []
        for m in mask_data:
            m["liaison_astronomers"] = liaison_astronomers[m["proposal_code_id"]]
            mask.append(m)
        return mask
