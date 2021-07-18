import json
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.proposal import ContactDetails, Proposal, ProposalSummary


class ProposalRepository:
    EXCLUDED_BLOCK_STATUS_VALUES = ["Deleted", "Superseded"]

    def __init__(self, connection: Connection, proposals_dir: Path):
        self.connection = connection
        self.proposals_dir = proposals_dir

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

    def get(self, proposal_code: str) -> Proposal:
        submission = self._current_submission(proposal_code)
        proposal_file = (
            self.proposals_dir / proposal_code / str(submission) / "Proposal.json"
        )
        with open(proposal_file) as f:
            proposal = json.load(f)

        proposal["blocks"] = self._blocks(proposal_code)
        proposal["observations"] = self._observations(proposal_code)
        return proposal

    def _current_submission(self, proposal_code: str) -> int:
        stmt = text(
            """
SELECT Submission
FROM Proposal
         JOIN ProposalCode PC on Proposal.ProposalCode_Id = PC.ProposalCode_Id
WHERE Current = 1
  AND Proposal_Code = :proposal_code
ORDER BY Submission DESC
LIMIT 1
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return int(result.scalar())

    def _blocks(self, proposal_code: str) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT B.Block_Id                      AS id,
       CONCAT(S.Year, '-', S.Semester) AS semester,
       B.Block_Name                    AS name,
       B.ObsTime                       AS observation_time,
       B.Priority                      AS priority,
       B.NVisits                       AS requested_observations,
       B.NDone                         AS accepted_observations,
       B.NAttempted                    AS rejected_observations,
       B.MaxSeeing                     AS max_seeing,
       T.Transparency                  AS transparency,
       B.MaxLunarPhase                 AS max_lunar_phase
FROM Block B
         JOIN Transparency T on B.Transparency_Id = T.Transparency_Id
         JOIN BlockStatus BS on B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN Proposal P ON B.Proposal_Id = P.Proposal_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND PC.Proposal_Code = :proposal_code
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )

        blocks = [dict(row) for row in result]
        block_targets = self._block_targets(proposal_code)
        block_instruments = self._block_instruments(proposal_code)
        for b in blocks:
            b["targets"] = block_targets[b["id"]]
            b["instruments"] = block_instruments[b["id"]]

        return blocks

    def _observations(self, proposal_code: str) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT BV.BlockVisit_Id     AS id,
       BV.Block_Id          AS block_id,
       NI.Date              AS night,
       BVS.BlockVisitStatus AS status,
       BRR.RejectedReason   AS rejection_reason
FROM BlockVisit BV
         JOIN BlockVisitStatus BVS ON BV.BlockVisitStatus_Id = BVS.BlockVisitStatus_Id
         LEFT JOIN BlockRejectedReason BRR on BV.BlockRejectedReason_Id = BRR.BlockRejectedReason_Id
         JOIN NightInfo NI on BV.NightInfo_Id = NI.NightInfo_Id
         JOIN Block B ON BV.Block_Id = B.Block_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return [dict(row) for row in result]

    def _block_targets(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of targets contained in the blocks.
        """
        separator = "::::"
        stmt = text(
            """
SELECT B.Block_Id                                                                       AS block_id,
       GROUP_CONCAT(DISTINCT T.Target_Name ORDER BY T.Target_Name SEPARATOR :separator) AS targets
FROM Target T
         JOIN Observation O on T.Target_Id = O.Target_Id
         JOIN Pointing P ON O.Pointing_Id = P.Pointing_Id
         JOIN Block B on P.Block_Id = B.Block_Id
         JOIN BlockStatus BS on B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )
        return {row.block_id: row.targets.split(separator) for row in result}

    def _block_salticam_modes(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of Salticam modes contained in the
        blocks.

        A block is only included in the dictionary if it is using Salticam. There is
        only one mode, which is an empty string.
        """
        stmt = text(
            """
SELECT B.Block_Id AS block_id
FROM ObsConfig OC
         JOIN PayloadConfig PC ON OC.PayloadConfig_Id = PC.PayloadConfig_Id
         JOIN PayloadConfigType PCT ON PC.PayloadConfigType_Id = PCT.PayloadConfigType_Id
         JOIN TelescopeConfigObsConfig TCOC ON OC.ObsConfig_Id = TCOC.PlannedObsConfig_Id
         JOIN Pointing P ON TCOC.Pointing_Id = P.Pointing_Id
         JOIN Block B ON P.Block_Id = B.Block_Id
         JOIN BlockStatus BS ON B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN ProposalCode C ON B.ProposalCode_Id = C.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND C.Proposal_Code = :proposal_code
  AND OC.SalticamPattern_Id IS NOT NULL
  AND PCT.Type != 'Acquisition'
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )
        return {row.block_id: [""] for row in result}

    def _block_rss_modes(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of RSS modes contained in the
        blocks.

        A block is only included in the dictionary if it is using RSS. The modes are
        ordered alphabetically for every block.
        """
        separator = "::::"
        stmt = text(
            """
SELECT B.Block_Id AS block_id,
       GROUP_CONCAT(DISTINCT RM.Mode ORDER BY RM.Mode SEPARATOR :separator) AS modes
FROM RssMode RM
         JOIN RssConfig RC on RM.RssMode_Id = RC.RssMode_Id
         JOIN Rss R on RC.RssConfig_Id = R.RssConfig_Id
         JOIN RssPatternDetail RPD on R.Rss_Id = RPD.Rss_Id
         JOIN RssPattern RP on RPD.RssPattern_Id = RP.RssPattern_Id
         JOIN ObsConfig OC on RP.RssPattern_Id = OC.RssPattern_Id
         JOIN TelescopeConfigObsConfig TCOC on OC.ObsConfig_Id = TCOC.PlannedObsConfig_Id
         JOIN Pointing P on TCOC.Pointing_Id = P.Pointing_Id
         JOIN Block B on P.Block_Id = B.Block_Id
         JOIN BlockStatus BS on B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )
        return {row.block_id: row.modes.split(separator) for row in result}

    def _block_hrs_modes(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of HRS modes contained in the
        blocks.

        A block is only included in the dictionary if it is using HRS. The modes are
        ordered alphabetically for every block.
        """
        separator = "::::"
        stmt = text(
            """
SELECT B.Block_Id AS block_id,
       GROUP_CONCAT(DISTINCT HM.ExposureMode ORDER BY HM.ExposureMode SEPARATOR :separator) AS modes
FROM HrsMode HM
         JOIN HrsConfig HC on HM.HrsMode_Id = HC.HrsMode_Id
         JOIN Hrs H ON HC.HrsConfig_Id = H.HrsConfig_Id
         JOIN HrsPatternDetail HPD on H.Hrs_Id = HPD.Hrs_Id
         JOIN HrsPattern HP on HPD.HrsPattern_Id = HP.HrsPattern_Id
         JOIN ObsConfig OC on HP.HrsPattern_Id = OC.HrsPattern_Id
         JOIN TelescopeConfigObsConfig TCOC on OC.ObsConfig_Id = TCOC.PlannedObsConfig_Id
         JOIN Pointing P on TCOC.Pointing_Id = P.Pointing_Id
         JOIN Block B on P.Block_Id = B.Block_Id
         JOIN BlockStatus BS on B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )

        return {
            row.block_id: [mode.title() for mode in row.modes.split(separator)]
            for row in result
        }

    def _block_bvit_modes(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of BVIT modes contained in the
        blocks.

        A block is only included in the dictionary if it is using BVIT. There is only
        one mode, which is an empty string.
        """
        stmt = text(
            """
SELECT B.Block_Id AS block_id
FROM ObsConfig OC
         JOIN TelescopeConfigObsConfig TCOC ON OC.ObsConfig_Id = TCOC.PlannedObsConfig_Id
         JOIN Pointing P ON TCOC.Pointing_Id = P.Pointing_Id
         JOIN Block B ON P.Block_Id = B.Block_Id
         JOIN BlockStatus BS ON B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN ProposalCode C ON B.ProposalCode_Id = C.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND C.Proposal_Code = :proposal_code
  AND OC.BvitPattern_Id IS NOT NULL
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
            },
        )
        return {row.block_id: [""] for row in result}

    def _block_instruments(self, proposal_code: str) -> Dict[int, List[Dict[str, Any]]]:
        salticam_modes = self._block_salticam_modes(proposal_code)
        rss_modes = self._block_rss_modes(proposal_code)
        hrs_modes = self._block_hrs_modes(proposal_code)
        bvit_modes = self._block_bvit_modes(proposal_code)

        instruments: DefaultDict[int, List[Dict[str, Any]]] = defaultdict(list)
        for block_id, m in salticam_modes.items():
            instruments[block_id].append({"name": "Salticam", "modes": m})
        for block_id, m in rss_modes.items():
            instruments[block_id].append({"name": "RSS", "modes": m})
        for block_id, m in hrs_modes.items():
            instruments[block_id].append({"name": "HRS", "modes": m})
        for block_id, m in bvit_modes.items():
            instruments[block_id].append({"name": "BVIT", "modes": m})

        return instruments
