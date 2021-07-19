from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, Dict, List, Optional, cast

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.proposal import ContactDetails, Proposal, ProposalSummary


class ProposalRepository:
    EXCLUDED_BLOCK_STATUS_VALUES = ["Deleted", "Superseded"]

    def __init__(self, connection: Connection):
        self.connection = connection

    def _list(self) -> List[ProposalSummary]:
        """
        Return a list of proposal summaries.
        """
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
        """
        Return a list of proposal summaries.
        """
        return self._list()

    def get(self, proposal_code: str, semester: Optional[str] = None) -> Proposal:
        """
        Return the proposal content for a semester.
        """
        if semester is None:
            semester = self._latest_submission_semester(proposal_code)
        submission = self._latest_submission(proposal_code, semester)

        block_targets = self._block_targets(proposal_code)
        proposal: Dict[str, Any] = {
            "general_info": self._general_info(proposal_code, submission),
            "investigators": self._investigators(proposal_code),
            "blocks": self._blocks(proposal_code, block_targets, semester),
            "executed_observations": self._executed_observations(
                proposal_code, block_targets
            ),
            "time_allocations": self.time_allocations(proposal_code, semester),
            "charged_time": self.charged_time(proposal_code, semester),
        }
        return proposal

    def _semesters(self, proposal_code: str) -> List[str]:
        """
        Return an ordered list of the semesters for which this a proposal has been
        submitted.
        """
        stmt = text(
            """
SELECT DISTINCT CONCAT(S.Year, '-', S.Semester) AS semester
FROM Semester S
         JOIN Proposal P ON S.Semester_Id = P.Semester_Id
         JOIN ProposalCode PC ON P.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
ORDER BY S.Year, S.Semester;
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return list(result.scalars())

    def _latest_submission_semester(self, proposal_code: str) -> str:
        """
        Return the semester for which the latest submission was made.
        """
        stmt = text(
            """
SELECT CONCAT(S.Year, '-', S.Semester) AS semester
FROM Proposal P
         JOIN ProposalCode PC ON P.ProposalCode_Id = PC.ProposalCode_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
WHERE PC.Proposal_Code = :proposal_code
  AND P.Current = 1
ORDER BY S.Year DESC, S.Semester DESC
LIMIT 1
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return cast(str, result.scalar_one())

    def _first_submission_date(self, proposal_code: str) -> datetime:
        """
        Return the date and time when the first submission was made.
        """
        stmt = text(
            """
SELECT P.SubmissionDate AS submission_date
FROM Proposal P
         JOIN ProposalCode PC ON P.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
  AND P.Submission = 1;
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return cast(datetime, result.scalar_one())

    def _latest_submission(self, proposal_code: str, semester: str) -> int:
        """
        Return the submission number of the latest submission for a semester.
        """
        year, sem = semester.split("-")
        stmt = text(
            """
SELECT Submission
FROM Proposal P
         JOIN ProposalCode PC on P.ProposalCode_Id = PC.ProposalCode_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
WHERE P.Current = 1
  AND PC.Proposal_Code = :proposal_code
  AND S.Year = :year
  AND S.Semester = :semester
ORDER BY Submission DESC
LIMIT 1
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "year": year, "semester": sem}
        )
        return cast(int, result.scalar())

    def _general_info(
        self, proposal_code: str, submission_number: int
    ) -> Dict[str, Any]:
        """
        Return general proposal information.
        """
        stmt = text(
            """
SELECT P.Proposal_Id                       AS id,
       PC.Proposal_Code                    AS code,
       CONCAT(S.Year, '-', S.Semester)     AS current_semester,
       PT.Title                            AS title,
       PT.Abstract                         AS abstract,
       PT.ReadMe                           AS summary_for_salt_astronomer,
       PT.NightlogSummary                  AS summary_for_night_log,
       P.SubmissionDate                    AS current_submission,
       P.Submission                        AS submission_number,
       P.Phase                             AS phase,
       PS.Status                           AS status,
       T.ProposalType                      AS type,
       PGI.ActOnAlert                      AS target_of_opportunity,
       P.TotalReqTime                      AS total_requested_time,
       PGI.ProprietaryPeriod               AS proprietary_period,
       CONCAT(I.FirstName, ' ', I.Surname) AS responsible_salt_astronomer
FROM Proposal P
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         JOIN ProposalCode PC ON P.ProposalCode_Id = PC.ProposalCode_Id
         JOIN ProposalText PT ON PC.ProposalCode_Id = PT.ProposalCode_Id AND S.Semester_Id = PT.Semester_Id
         JOIN ProposalGeneralInfo PGI ON PC.ProposalCode_Id = PGI.ProposalCode_Id
         JOIN ProposalType T ON PGI.ProposalType_Id = T.ProposalType_Id
         JOIN ProposalStatus PS ON PGI.ProposalStatus_Id = PS.ProposalStatus_Id
         JOIN ProposalContact C ON PC.ProposalCode_Id = C.ProposalCode_Id
         JOIN Investigator I ON C.Astronomer_Id = I.Investigator_Id
WHERE PC.Proposal_Code = :proposal_code
  AND P.Submission = :submission
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "submission": submission_number}
        )
        info = dict(result.one())

        if info["type"] == "Director Discretionary Time (DDT)":
            info["type"] = "Director's Discretionary Time"

        info["first_submission"] = self._first_submission_date(proposal_code)
        info["semesters"] = self._semesters(proposal_code)

        return info

    def _investigators(self, proposal_code: str) -> List[Dict[str, Any]]:
        """
        Return the list of investigators.

        The list is ordered by family nme and given name.
        """
        stmt = text(
            """
SELECT PU.PiptUser_Id          AS id,
       I.FirstName             AS given_name,
       I.Surname               AS family_name,
       P.Partner_Name          AS partner,
       `IN`.InstituteName_Name AS institute,
       I2.Department           AS department,
       PI.InvestigatorOkay     AS approved,
       PI.ApprovalCode         AS approval_code
FROM ProposalInvestigator PI
         JOIN Investigator I ON PI.Investigator_Id = I.Investigator_Id
         JOIN PiptUser PU ON I.PiptUser_Id = PU.PiptUser_Id
         JOIN Institute I2 ON I.Institute_Id = I2.Institute_Id
         JOIN Partner P ON I2.Partner_Id = P.Partner_Id
         JOIN InstituteName `IN` ON I2.InstituteName_Id = `IN`.InstituteName_Id
         JOIN ProposalCode PC ON PI.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
ORDER BY I.Surname, I.FirstName
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        investigators = [dict(row) for row in result]

        pi_id = self._principal_investigator_user_id(proposal_code)
        pc_id = self._principal_contact_user_id(proposal_code)

        for investigator in investigators:
            investigator["is_pi"] = investigator["id"] == pi_id
            investigator["is_pc"] = investigator["id"] == pc_id

            if investigator["approved"] == 1:
                investigator["approved_proposal"] = True
            elif (
                investigator["approval_code"] is None
                or investigator["approval_code"] == ""
            ):
                investigator["approved_proposal"] = False
            else:
                investigator["approved_proposal"] = None

            del investigator["approved"]
            del investigator["approval_code"]

        return investigators

    def _principal_investigator_user_id(self, proposal_code: str) -> int:
        """
        Return the user id of the Principal Investigator.
        """
        stmt = text(
            """
SELECT I.PiptUser_Id
FROM ProposalContact PC
         JOIN Investigator I ON PC.Leader_Id = I.Investigator_Id
         JOIN ProposalCode P ON PC.ProposalCode_Id = P.ProposalCode_Id
WHERE P.Proposal_Code = :proposal_code
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return cast(int, result.scalar_one())

    def _principal_contact_user_id(self, proposal_code: str) -> int:
        """
        Return the user id of the Principal Contact.
        """
        stmt = text(
            """
SELECT I.PiptUser_Id
FROM ProposalContact PC
         JOIN Investigator I ON PC.Contact_Id = I.Investigator_Id
         JOIN ProposalCode P ON PC.ProposalCode_Id = P.ProposalCode_Id
WHERE P.Proposal_Code = :proposal_code
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        return cast(int, result.scalar_one())

    def _blocks(
        self, proposal_code: str, block_targets: Dict[int, List[str]], semester: str
    ) -> List[Dict[str, Any]]:
        """
        Return the blocks for a semester.
        """
        year, sem = semester.split("-")
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
       B.MaxSeeing                     AS maximum_seeing,
       T.Transparency                  AS transparency,
       B.MaxLunarPhase                 AS maximum_lunar_phase
FROM Block B
         JOIN Transparency T on B.Transparency_Id = T.Transparency_Id
         JOIN BlockStatus BS on B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN Proposal P ON B.Proposal_Id = P.Proposal_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE BS.BlockStatus NOT IN :excluded_status_values
  AND PC.Proposal_Code = :proposal_code
  AND S.Year = :year
  AND S.Semester = :semester
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "excluded_status_values": self.EXCLUDED_BLOCK_STATUS_VALUES,
                "proposal_code": proposal_code,
                "year": year,
                "semester": sem,
            },
        )

        blocks = [dict(row) for row in result]
        block_instruments = self._block_instruments(proposal_code)
        for b in blocks:
            b["targets"] = block_targets[b["id"]]
            b["instruments"] = block_instruments[b["id"]]

        return blocks

    def _executed_observations(
        self, proposal_code: str, block_targets: Dict[int, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Return the executed observations (including observatiopns in the queue) for all
        semesters.

        The observations are ordered by block name and observation night.
        """
        stmt = text(
            """
SELECT BV.BlockVisit_Id     AS id,
       BV.Block_Id          AS block_id,
       B.Block_Name AS block_name,
       B.ObsTime AS observation_time,
       B.Priority AS priority,
       B.MaxLunarPhase AS maximum_lunar_phase,
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
ORDER BY B.Block_Name, NI.Date
        """
        )
        result = self.connection.execute(stmt, {"proposal_code": proposal_code})
        observations = [dict(row) for row in result]

        for observation in observations:
            observation["targets"] = block_targets[observation["block_id"]]

        return observations

    def _block_targets(self, proposal_code: str) -> Dict[int, List[str]]:
        """
        Return the dictionary of block ids and lists of targets contained in the blocks
        for all semesters.
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
WHERE PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
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
         JOIN ProposalCode C ON B.ProposalCode_Id = C.ProposalCode_Id
WHERE C.Proposal_Code = :proposal_code
  AND OC.SalticamPattern_Id IS NOT NULL
  AND PCT.Type != 'Acquisition'
        """
        )
        result = self.connection.execute(
            stmt,
            {
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
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
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
         JOIN ProposalCode PC on B.ProposalCode_Id = PC.ProposalCode_Id
WHERE PC.Proposal_Code = :proposal_code
GROUP BY B.Block_Id
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "separator": separator,
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
         JOIN ProposalCode C ON B.ProposalCode_Id = C.ProposalCode_Id
WHERE C.Proposal_Code = :proposal_code
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
        """
        Return the dictionary of block ids and dictionaries of instruments and modes.
        """
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

    def time_allocations(
        self, proposal_code: str, semester: str
    ) -> List[Dict[str, Any]]:
        """
        Return the time allocations and TAC comments for a semester.
        """
        allocations = self._allocations(proposal_code, semester)
        comments = self._tac_comments(proposal_code, semester)
        partners = set([alloc["partner"] for alloc in allocations])
        partners.update(comments.keys())

        # combine the time allocations and comments by partner
        combined: Dict[str, Dict[str, Any]] = {
            partner: {
                "partner": partner,
                "priority_0": 0,
                "priority_1": 0,
                "priority_2": 0,
                "priority_3": 0,
                "priority_4": 0,
                "tac_comment": None,
            }
            for partner in partners
        }
        for partner, comment in comments.items():
            combined[partner]["tac_comment"] = comment
        for alloc in allocations:
            combined[alloc["partner"]][f"priority_{alloc['priority']}"] = alloc[
                "time_allocation"
            ]

        return list(combined.values())

    def _allocations(self, proposal_code: str, semester: str) -> List[Dict[str, Any]]:
        """
        Return the time allocations for a semester.
        """
        year, sem = semester.split("-")
        stmt = text(
            """
SELECT P.Partner_Name AS partner, PA.Priority AS priority, SUM(PA.TimeAlloc) AS time_allocation
FROM PriorityAlloc PA
         JOIN MultiPartner MP ON PA.MultiPartner_Id = MP.MultiPartner_Id
         JOIN ProposalCode PC ON MP.ProposalCode_Id = PC.ProposalCode_Id
         JOIN Semester S ON MP.Semester_Id = S.Semester_Id
         JOIN Partner P ON MP.Partner_Id = P.Partner_Id
WHERE PC.Proposal_Code = :proposal_code
  AND S.Year = :year
  AND S.Semester = :semester
GROUP BY PA.MultiPartner_Id, PA.Priority
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "year": year, "semester": sem}
        )
        return [dict(row) for row in result]

    def _tac_comments(self, proposal_code: str, semester: str) -> Dict[str, str]:
        """
        Return the TAC comments for a semester.
        """
        year, sem = semester.split("-")
        stmt = text(
            """
SELECT P.Partner_Name AS partner, TPC.TacComment AS tac_comment
FROM TacProposalComment TPC
         JOIN MultiPartner MP ON TPC.MultiPartner_Id = MP.MultiPartner_Id
         JOIN Partner P ON MP.Partner_Id = P.Partner_Id
         JOIN ProposalCode PC ON MP.ProposalCode_Id = PC.ProposalCode_Id
         JOIN Semester S ON MP.Semester_Id = S.Semester_Id
WHERE PC.Proposal_Code = :proposal_code
  AND S.Year = :year
  AND S.Semester = :semester
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "year": year, "semester": sem}
        )
        return {
            row.partner: row.tac_comment if row.tac_comment else None for row in result
        }

    def charged_time(self, proposal_code: str, semester: str) -> Dict[str, int]:
        year, sem = semester.split("-")
        stmt = text(
            """
SELECT B.Priority AS priority, SUM(B.ObsTime) AS charged_time
FROM BlockVisit BV
JOIN BlockVisitStatus BVS ON BV.BlockVisitStatus_Id = BVS.BlockVisitStatus_Id
JOIN Block B ON BV.Block_Id = B.Block_Id
JOIN Proposal P ON B.Proposal_Id = P.Proposal_Id
JOIN ProposalCode PC ON B.ProposalCode_Id = PC.ProposalCode_Id
JOIN Semester S ON P.Semester_Id = S.Semester_Id
WHERE PC.Proposal_Code = :proposal_code AND S.Year = :year AND S.Semester = :semester AND BVS.BlockVisitStatus = 'Accepted'
GROUP BY B.Priority
        """
        )
        result = self.connection.execute(
            stmt, {"proposal_code": proposal_code, "year": year, "semester": sem}
        )

        time: Dict[str, int] = {f"priority_{p}": 0 for p in range(5)}
        for row in result:
            time[f"priority_{row.priority}"] = row.charged_time

        return time
