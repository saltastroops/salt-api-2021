from datetime import datetime
from typing import Any, Optional, Dict, List, Tuple, cast

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.util import list_search


class MosRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def _get(self, semester_ids: Tuple[int]) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT DISTINCT
    P.Proposal_Id       proposal_id,
    Proposal_Code       proposal_code,
    PC.ProposalCode_Id  proposal_code_id,
    PI.Surname          pi_surname,
    BlockStatus         block_status,
    `Status`            status,
    Block_Name          block_name,
    Priority            priority,
    NVisits             n_visits,
    NDone               n_done,
    RssMask_Id          mask_id,
    Barcode             barcode,
    15.0 * RaH + 15.0 * RaM / 60.0 + 15.0 * RaS / 3600.0    ra_centre,
    CutBy               cut_by,
    CutDate             cut_date,
    SaComment           sa_comment
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
    AND P.Semester_Id IN :semester_ids
ORDER BY P.Semester_Id ASC, Proposal_Code ASC, Proposal_Id DESC
        """
        )
        results = self.connection.execute(stmt, {"semester_ids": tuple(semester_ids)})

        proposal_code_ids = []
        mask_data = []
        for row in results:
            mask_data.append(dict(row))
            proposal_code_ids.append(row.proposal_code_id)

        qsla = text("""
SELECT DISTINCT 
    ProposalCode_Id proposal_code_id, 
    Surname         surname
FROM Proposal
    JOIN ProposalContact PCO USING (ProposalCode_Id)
    JOIN Investigator I ON (PCO.Astronomer_Id=I.Investigator_Id)
WHERE ProposalCode_Id IN :proposal_code_ids
        """)
        results = self.connection.execute(qsla, {"proposal_code_ids": tuple(proposal_code_ids)})
        liaison_astronomers = [dict(row) for row in results]

        mask = []
        for m in mask_data:
            la = list_search(
                liaison_astronomers,
                m["proposal_code_id"],
                "proposal_code_id"
            )
            m["liaison_astronomers"] = la["surname"]
            mask.append(m)
        return mask

    def _get_mask_in_magazine(self):
        """
        The list is slit masks on the magazine
        """
        stmt = text(
            """
SELECT Barcode barcode
FROM RssCurrentMasks RCM 
    JOIN RssMask RM ON RCM.RssMask_Id = RM.RssMask_Id 
        """
        )
        results = self.connection.execute(stmt, {})

        return [row.barcode for row in results]

    def get(
            self,
            semester: str,
            include_next_semester: Optional[bool],
            include_previous_semester: Optional[bool]
    ) -> Dict[str, List]:
        qsid = text(
            """
SELECT Semester_Id FROM Semester semester WHERE CONCAT(Year, "-", Semester) = :semester          
        """
        )
        result = self.connection.execute(qsid, {"semester": semester})
        semester_ids = result.one()
        semester_id = semester_ids[0]

        if include_next_semester:
            semester_ids.append(semester_id + 1)
        if include_previous_semester:
            semester_ids.append(semester_id - 1)

        return {
            "mos_data":  self._get(semester_ids),
            "current_mask": self._get_mask_in_magazine()
        }


