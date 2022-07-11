from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, cast

import pytz
from astropy.coordinates import Angle
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError, NoResultFound

from saltapi.exceptions import NotFoundError
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.service.block import Block
from saltapi.service.proposal import ProposalCode


class BlockRepository:
    def __init__(
        self,
        target_repository: TargetRepository,
        instrument_repository: InstrumentRepository,
        connection: Connection,
    ) -> None:
        self.target_repository = target_repository
        self.instrument_repository = instrument_repository
        self.connection = connection

    def get(self, block_id: int) -> Block:
        """
        Return the block content for a block id.
        """

        # Avoid blocks with subblocks or subsubblocks.
        if self._has_subblock_or_subsubblock_iterations(block_id):
            error = (
                "Blocks which have subblock or subsubblock iterations are not "
                "supported"
            )
            raise ValueError(error)

        stmt = text(
            """
SELECT B.Block_Id                      AS block_id,
       BC.BlockCode                    AS code,
       B.Block_Name                    AS name,
       PC.Proposal_Code                AS proposal_code,
       P.SubmissionDate                AS submission_date,
       CONCAT(S.Year, '-', S.Semester) AS semester,
       BS.BlockStatus                  AS status,
       B.Priority                      AS priority,
       PR.Ranking                      AS ranking,
       B.WaitDays                      AS wait_period,
       B.NVisits                       AS requested_observations,
       B.NDone                         AS accepted_observations,
       B.NAttempted                    AS rejected_observations,
       B.Comments                      AS comment,
       B.MinSeeing                     AS minimum_seeing,
       B.MaxSeeing                     AS maximum_seeing,
       T.Transparency                  AS transparency,
       B.MaxLunarPhase                 AS maximum_lunar_phase,
       B.MinLunarAngularDistance       AS minimum_lunar_distance,
       B.ObsTime                       AS observation_time,
       B.OverheadTime                  AS overhead_time,
       BP.MoonProbability              AS moon_probability,
       BP.CompetitionProbability       AS competition_probability,
       BP.ObservabilityProbability     AS observability_probability,
       BP.SeeingProbability            AS seeing_probability,
       BP.AveRanking                   AS average_ranking,
       BP.TotalProbability             AS total_probability,
       B.BlockStatusReason             AS reason
FROM Block B
         JOIN BlockStatus BS ON B.BlockStatus_Id = BS.BlockStatus_Id
         LEFT JOIN PiRanking PR ON B.PiRanking_Id = PR.PiRanking_Id
         JOIN Transparency T ON B.Transparency_Id = T.Transparency_Id
         JOIN Proposal P ON B.Proposal_Id = P.Proposal_Id
         JOIN ProposalCode PC ON P.ProposalCode_Id = PC.ProposalCode_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         LEFT JOIN BlockProbabilities BP ON B.Block_Id = BP.Block_Id
         LEFT JOIN BlockCode BC ON B.BlockCode_Id = BC.BlockCode_Id
WHERE B.Block_Id = :block_id;
        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})

        row = result.one()

        observing_conditions = {
            "minimum_seeing": row.minimum_seeing,
            "maximum_seeing": row.maximum_seeing,
            "transparency": row.transparency,
            "minimum_lunar_distance": row.minimum_lunar_distance,
            "maximum_lunar_phase": row.maximum_lunar_phase,
        }
        observation_probabilities = {
            "moon": row.moon_probability,
            "competition": row.competition_probability,
            "observability": row.observability_probability,
            "seeing": row.seeing_probability,
            "average_ranking": row.average_ranking,
            "total": row.total_probability,
        }

        block = {
            "id": row.block_id,
            "code": row.code,
            "name": row.name,
            "proposal_code": row.proposal_code,
            "submission_date": pytz.utc.localize(row.submission_date),
            "semester": row.semester,
            "status": {
                "value": row.status if row.status != "On Hold" else "On hold",
                "reason": row.reason,
            },
            "priority": row.priority,
            "ranking": row.ranking,
            "wait_period": row.wait_period,
            "requested_observations": row.requested_observations,
            "accepted_observations": row.accepted_observations,
            "rejected_observations": row.rejected_observations,
            "comment": row.comment,
            "observing_conditions": observing_conditions,
            "observation_time": row.observation_time,
            "overhead_time": row.overhead_time,
            "observation_probabilities": observation_probabilities,
            "observing_windows": self._observing_windows(block_id),
            "block_visits": self._block_visits(block_id),
            "observations": self._pointings(block_id),
        }

        return block

    def get_block_status(self, block_id: int) -> Dict[str, Any]:
        """
        Return the block status for a block id.
        """
        stmt = text(
            """
SELECT BS.BlockStatus AS value, B.BlockStatusReason AS reason
FROM BlockStatus BS
         JOIN Block B ON BS.BlockStatus_Id = B.BlockStatus_Id
WHERE B.Block_Id = :block_id
        """
        )

        result = self.connection.execute(stmt, {"block_id": block_id})

        row = result.one()

        value = row.value
        if value == "On Hold":
            value = "On hold"
        status = {"value": value, "reason": row.reason}

        return status

    def update_block_status(
        self, block_id: int, value: str, reason: Optional[str]
    ) -> None:
        """
        Update the status of a block.
        """
        if value == "On hold":
            value = "On Hold"

        stmt = text(
            """
UPDATE Block B
SET B.BlockStatus_Id = (SELECT BS.BlockStatus_Id
                        FROM BlockStatus BS
                        WHERE BS.BlockStatus = :status),
    B.BlockStatusReason = :reason
WHERE B.Block_Id = :block_id;
    """
        )
        try:
            result = self.connection.execute(
                stmt, {"block_id": block_id, "status": value, "reason": reason}
            )
        except IntegrityError:
            raise ValueError("Unknown block status")
        if not result.rowcount:
            raise NotFoundError("Unknown block id")

    def get_proposal_code_for_block_id(self, block_id: int) -> str:
        """
        Return proposal code for a block id:
        """
        stmt = text(
            """
SELECT PC.Proposal_code
FROM ProposalCode PC
         JOIN Block B ON PC.ProposalCode_Id = B.ProposalCode_Id
WHERE B.Block_Id = :block_id;
    """
        )
        result = self.connection.execute(
            stmt,
            {"block_id": block_id},
        )

        try:
            return result.scalar_one()
        except NoResultFound:
            raise NotFoundError()

    def get_block_visit(self, block_visit_id: int) -> Dict[str, str]:
        """
        Return the block visits for a block visit id.
        """
        stmt = text(
            """
SELECT BV.BlockVisit_Id     AS id,
       NI.Date              AS night,
       BVS.BlockVisitStatus AS status,
       BRR.RejectedReason   AS rejection_reason
FROM BlockVisit BV
    LEFT JOIN BlockRejectedReason BRR
                   ON BV.BlockRejectedReason_Id = BRR.BlockRejectedReason_Id
    JOIN NightInfo NI ON BV.NightInfo_Id = NI.NightInfo_Id
    JOIN BlockVisitStatus BVS ON BV.BlockVisitStatus_Id = BVS.BlockVisitStatus_Id
WHERE BV.BlockVisit_Id = :block_visit_id
  AND BVS.BlockVisitStatus NOT IN ('Deleted');
        """
        )
        try:
            result = self.connection.execute(stmt, {"block_visit_id": block_visit_id})
            row = result.one()
            block_visit = {
                "id": row.id,
                "night": row.night,
                "status": row.status,
                "rejection_reason": row.rejection_reason,
            }
            return block_visit
        except NoResultFound:
            raise NotFoundError("Unknown block visit id")

    def update_block_visit_status(
        self, block_visit_id: int, status: str, rejection_reason: Optional[str]
    ) -> None:
        """
        Update the status of a block visit.
        """

        if not self._block_visit_exists(block_visit_id):
            raise NotFoundError(f"Unknown block visit id: {block_visit_id}")
        try:
            block_visit_status_id = self._block_visit_status_id(status)
            block_rejected_reason_id = (
                self._block_rejection_reason_id(rejection_reason)
                if rejection_reason
                else None
            )
        except NoResultFound:
            raise ValueError(f"Unknown block visit status: {status}")
        stmt = text(
            """
UPDATE BlockVisit BV
SET BV.BlockVisitStatus_Id = :block_visit_status_id,
    BV.BlockRejectedReason_Id = :block_rejected_reason_id
WHERE BV.BlockVisit_Id = :block_visit_id
AND BV.BlockVisitStatus_Id NOT IN (SELECT BVS2.BlockVisitStatus_Id
                                    FROM BlockVisitStatus AS BVS2
                                    WHERE BVS2.BlockVisitStatus = 'Deleted');
        """
        )
        self.connection.execute(
            stmt,
            {
                "block_visit_id": block_visit_id,
                "block_visit_status_id": block_visit_status_id,
                "block_rejected_reason_id": block_rejected_reason_id,
            },
        )

    def _block_visit_status_id(self, status: str) -> int:
        stmt = text(
            """
SELECT BVS.BlockVisitStatus_Id AS id
FROM BlockVisitStatus BVS
WHERE BVS.BlockVisitStatus = :status
        """
        )
        result = self.connection.execute(stmt, {"status": status})
        return cast(int, result.scalar_one())

    def _block_rejection_reason_id(self, rejection_reason: str) -> int:
        stmt = text(
            """
SELECT BRR.BlockRejectedReason_Id AS id
FROM BlockRejectedReason BRR
WHERE BRR.RejectedReason = :rejected_reason
        """
        )
        result = self.connection.execute(stmt, {"rejected_reason": rejection_reason})
        return cast(int, result.scalar_one())

    def _block_visit_exists(self, block_visit_id: int) -> bool:
        stmt = text(
            """
SELECT COUNT(*) FROM BlockVisit WHERE BlockVisit_Id = :block_visit_id
        """
        )
        result = self.connection.execute(stmt, {"block_visit_id": block_visit_id})

        return cast(int, result.scalar_one()) > 0

    def get_proposal_code_for_block_visit_id(self, block_visit_id: int) -> ProposalCode:
        """
        Return proposal code for a block visit id:
        """
        stmt = text(
            """
SELECT PC.Proposal_code
FROM ProposalCode PC
         JOIN Block B ON PC.ProposalCode_Id = B.ProposalCode_Id
         JOIN BlockVisit BV ON BV.Block_Id = B.Block_Id
         JOIN BlockVisitStatus BVS ON BV.BlockVisitStatus_Id = BVS.BlockVisitStatus_Id
WHERE BV.BlockVisit_Id = :block_visit_id
  AND BVS.BlockVisitStatus NOT IN ('Deleted');
        """
        )
        result = self.connection.execute(
            stmt,
            {"block_visit_id": block_visit_id},
        )

        try:
            return cast(ProposalCode, result.scalar_one())
        except NoResultFound:
            raise NotFoundError()

    def _block_visits(self, block_id: int) -> List[Dict[str, Any]]:
        """
        Return the executed observations.
        """
        stmt = text(
            """
SELECT BV.BlockVisit_Id     AS id,
       NI.Date              AS night,
       BVS.BlockVisitStatus AS status,
       BRR.RejectedReason   AS rejection_reason
FROM BlockVisit BV
         JOIN BlockVisitStatus BVS ON BV.BlockVisitStatus_Id = BVS.BlockVisitStatus_Id
         LEFT JOIN BlockRejectedReason BRR
                   ON BV.BlockRejectedReason_Id = BRR.BlockRejectedReason_Id
         JOIN NightInfo NI ON BV.NightInfo_Id = NI.NightInfo_Id
         JOIN Block B ON BV.Block_Id IN (
    SELECT B1.Block_Id
    FROM Block B1
    WHERE B1.BlockCode_Id = B.BlockCode_Id
)
WHERE B.Block_Id = :block_id
  AND BVS.BlockVisitStatus IN ('Accepted', 'Rejected');
        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})
        block_visits = [
            {
                "id": row.id,
                "night": row.night,
                "status": row.status,
                "rejection_reason": row.rejection_reason,
            }
            for row in result
        ]

        return block_visits

    def _observing_windows(self, block_id: int) -> List[Dict[str, datetime]]:
        """
        Return the observing windows.
        """
        stmt = text(
            """
SELECT BVW.VisibilityStart AS start, BVW.VisibilityEnd AS end
FROM BlockVisibilityWindow BVW
WHERE BVW.Block_Id = :block_id
ORDER BY BVW.VisibilityStart;
        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})
        return [
            {"start": pytz.utc.localize(row.start), "end": pytz.utc.localize(row.end)}
            for row in result
        ]

    def _finder_charts(self, pointing_id: int) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT FC.FindingChart_Id AS finding_chart_id,
       FC.Comments        AS comments,
       FC.ValidFrom       AS valid_from,
       FC.ValidUntil      AS valid_until
FROM FindingChart FC
WHERE FC.Pointing_Id = :pointing_id
ORDER BY ValidFrom, FindingChart_Id
        """
        )
        result = self.connection.execute(stmt, {"pointing_id": pointing_id})

        return [
            {
                "id": row.finding_chart_id,
                "comment": row.comments,
                "valid_from": pytz.utc.localize(row.valid_from)
                if row.valid_from
                else None,
                "valid_until": pytz.utc.localize(row.valid_until)
                if row.valid_until
                else None,
            }
            for row in result
        ]

    def _time_restrictions(
        self, pointing_id: int
    ) -> Optional[List[Dict[str, datetime]]]:
        """
        Return the time restrictions.
        """
        stmt = text(
            """
SELECT DISTINCT TR.ObsWindowStart AS start, TR.ObsWindowEnd AS end
FROM TimeRestricted TR
         JOIN Pointing P ON TR.Pointing_Id = P.Pointing_Id
WHERE P.Pointing_Id = :pointing_id
ORDER BY TR.ObsWindowStart;
        """
        )
        result = self.connection.execute(stmt, {"pointing_id": pointing_id})
        restrictions = [
            {"start": pytz.utc.localize(row.start), "end": pytz.utc.localize(row.end)}
            for row in result
        ]

        return restrictions if len(restrictions) else None

    def _phase_constraints(self, pointing_id: int) -> Optional[List[Dict[str, float]]]:
        """
        Return the phase constraints.
        """
        stmt = text(
            """
SELECT PC.PhaseStart AS start, PC.PhaseEnd AS end
FROM PhaseConstraint PC
WHERE PC.Pointing_Id = :pointing_id
ORDER BY PC.PhaseStart;
        """
        )
        result = self.connection.execute(stmt, {"pointing_id": pointing_id})
        constraints = [dict(row) for row in result]

        return constraints if len(constraints) else None

    def _pointings(self, block_id: int) -> List[Dict[str, Any]]:
        """
        Return the pointings.
        """
        stmt = text(
            """
SELECT P.Pointing_Id                                                  AS pointing_id,
       P.ObsTime                                                      AS observation_time,
       P.OverheadTime                                                 AS overhead_time,
       TCOC.Observation_Order                                         AS observation_order,
       TCOC.TelescopeConfig_Order                                     AS telescope_config_order,
       TCOC.PlannedObsConfig_Order                                    AS planned_obsconfig_order,
       O.Target_Id                                                    AS target_id,
       TC.PositionAngle                                               AS position_angle,
       TC.UseParallacticAngle                                         AS use_parallactic_angle,
       TC.Iterations                                                  AS tc_iterations,
       DP.DitherPatternDescription                                    AS dp_description,
       DP.NHorizontalTiles                                            AS dp_horizontal_tiles,
       DP.NVerticalTiles                                              AS dp_vertical_tiles,
       DP.Offsetsize                                                  AS dp_offset_size,
       DP.NSteps                                                      AS dp_steps,
       CONCAT(GS.RaH, ':', GS.RaM, ':', GS.RaS / 1000)                AS gs_ra,
       CONCAT(GS.DecSign, GS.DecD, ':', GS.DecM, ':', GS.DecS / 1000) AS gs_dec,
       GS.Equinox                                                     AS gs_equinox,
       GS.Mag                                                         AS gs_magnitude,
       L.Lamp                                                         AS pc_lamp,
       CF.CalFilter                                                   AS pc_calibration_filter,
       GM.GuideMethod                                                 AS pc_guide_method,
       PCT.Type                                                       AS pc_type,
       PC.CalScreenIn                                                 AS pc_calibration_screen_in,
       OC.SalticamPattern_Id                                          AS salticam_pattern_id,
       OC.RssPattern_Id                                               AS rss_pattern_id,
       OC.HrsPattern_Id                                               AS hrs_pattern_id,
       OC.BvitPattern_Id                                              AS bvit_pattern_id
FROM TelescopeConfigObsConfig TCOC
         JOIN Pointing P ON TCOC.Pointing_Id = P.Pointing_Id
         JOIN Block B ON P.Block_Id = B.Block_Id
         JOIN TelescopeConfig TC ON TCOC.Pointing_Id = TC.Pointing_Id AND
                                    TCOC.Observation_Order = TC.Observation_Order AND
                                    TCOC.TelescopeConfig_Order =
                                    TC.TelescopeConfig_Order
         LEFT JOIN DitherPattern DP ON TC.DitherPattern_Id = DP.DitherPattern_Id
         LEFT JOIN GuideStar GS ON TC.GuideStar_Id = GS.GuideStar_Id
         JOIN Observation O ON TCOC.Pointing_Id = O.Pointing_Id AND
                               TCOC.Observation_Order = O.Observation_Order
         JOIN Target T ON O.Target_Id = T.Target_Id
         JOIN ObsConfig OC ON TCOC.PlannedObsConfig_Id = OC.ObsConfig_Id
         JOIN PayloadConfig PC ON OC.PayloadConfig_Id = PC.PayloadConfig_Id
         LEFT JOIN Lamp L ON PC.Lamp_Id = L.Lamp_Id
         LEFT JOIN CalFilter CF ON PC.CalFilter_Id = CF.CalFilter_Id
         LEFT JOIN GuideMethod GM ON PC.GuideMethod_Id = GM.GuideMethod_Id
         LEFT JOIN PayloadConfigType PCT
                   ON PC.PayloadConfigType_Id = PCT.PayloadConfigType_Id
WHERE B.Block_Id = :block_id
ORDER BY TCOC.Pointing_Id, TCOC.Observation_Order, TCOC.TelescopeConfig_Order,
         TCOC.PlannedObsConfig_Order;
        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})

        # collect the pointings
        pointing_groups = self._group_by_pointing_id(result)

        # avoid pointings with multiple observations
        for pointing_rows in pointing_groups:
            if self._has_multiple_observations(pointing_rows[0].pointing_id):
                error = (
                    "Blocks containing a pointing with multiple observations are "
                    "not supported."
                )
                raise ValueError(error)

        # create the pointings
        pointings: List[Dict[str, Any]] = []
        for pointing_rows in pointing_groups:
            pointing = {
                "target": self.target_repository.get(pointing_rows[0].target_id),
                "finder_charts": self._finder_charts(pointing_rows[0].pointing_id),
                "time_restrictions": self._time_restrictions(
                    pointing_rows[0].pointing_id
                ),
                "phase_constraints": self._phase_constraints(
                    pointing_rows[0].pointing_id
                ),
                "telescope_configurations": self._telescope_configurations(
                    pointing_rows
                ),
                "observation_time": pointing_rows[0].observation_time,
                "overhead_time": pointing_rows[0].overhead_time
                if pointing_rows[0].overhead_time
                else None,
            }
            pointings.append(pointing)

        return pointings

    def _group_by_pointing_id(self, rows: Iterable[Any]) -> List[List[Any]]:
        """
        Group rows obtained in the _pointings method by pointing order.
        """
        previous_pointing_id = None
        current_pointing_rows: List[Any] = []
        pointings = []
        for row in rows:
            if row.pointing_id != previous_pointing_id:
                current_pointing_rows = []
                pointings.append(current_pointing_rows)
            current_pointing_rows.append(row)
            previous_pointing_id = row.pointing_id

        return pointings

    def _dither_pattern(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Return the dither pattern.
        """
        if row["dp_horizontal_tiles"] is None:
            return None

        return {
            "horizontal_tiles": row["dp_horizontal_tiles"],
            "vertical_tiles": row["dp_vertical_tiles"],
            "offset_size": row["dp_offset_size"],
            "steps": row["dp_steps"],
            "description": row["dp_description"],
        }

    def _guide_star(self, row: Any) -> Optional[Dict[str, Any]]:
        """
        Return the guide star.
        """

        ra = Angle(f"{row.gs_ra} hours").degree
        dec = Angle(f"{row.gs_dec} degrees").degree

        if ra == 0 and dec == 0:
            return None

        return {
            "right_ascension": ra,
            "declination": dec,
            "equinox": row.gs_equinox,
            "magnitude": row.gs_magnitude,
        }

    def _telescope_configurations(self, pointing_rows: List[Any]) -> List[Any]:
        """
        Get the list of telescope configurations for database rows belonging to a
        pointing.
        """
        # Group the rows by telescope config
        previous_telescope_config_order = None
        current_telescope_config_rows: List[Any] = []
        tc_groups = []
        for row in pointing_rows:
            if row.telescope_config_order != previous_telescope_config_order:
                current_telescope_config_rows = []
                tc_groups.append(current_telescope_config_rows)
            current_telescope_config_rows.append(row)

            previous_telescope_config_order = row.telescope_config_order

        # Create the telescope configurations
        telescope_configs = []
        for tc_group in tc_groups:
            row = tc_group[0]
            tc = {
                "iterations": row["tc_iterations"],
                "position_angle": row["position_angle"],
                "use_parallactic_angle": row["use_parallactic_angle"],
                "dither_pattern": self._dither_pattern(row),
                "guide_star": self._guide_star(row),
                "payload_configurations": [
                    self._payload_configuration(row) for row in tc_group
                ],
            }
            telescope_configs.append(tc)

        return telescope_configs

    def _payload_configuration(self, payload_config_row: Any) -> Dict[str, Any]:
        payload_config = {
            "payload_configuration_type": payload_config_row.pc_type,
            "use_calibration_screen": True
            if payload_config_row.pc_calibration_screen_in
            else False,
            "lamp": payload_config_row.pc_lamp,
            "calibration_filter": payload_config_row.pc_calibration_filter,
            "guide_method": payload_config_row.pc_guide_method,
            "instruments": self._instruments(payload_config_row),
        }

        return payload_config

    def _instruments(
        self, payload_config_row: Any
    ) -> Dict[str, Optional[List[Dict[str, Any]]]]:
        if payload_config_row.salticam_pattern_id is not None:
            salticam_setups: Optional[List[Dict[str, Any]]] = self._salticam_setups(
                payload_config_row.salticam_pattern_id
            )
        else:
            salticam_setups = None
        if payload_config_row.rss_pattern_id is not None:
            rss_setups: Optional[List[Dict[str, Any]]] = self._rss_setups(
                payload_config_row.rss_pattern_id
            )
        else:
            rss_setups = None
        if payload_config_row.hrs_pattern_id is not None:
            hrs_setups: Optional[List[Dict[str, Any]]] = self._hrs_setups(
                payload_config_row.hrs_pattern_id
            )
        else:
            hrs_setups = None
        if payload_config_row.bvit_pattern_id is not None:
            bvit_setups: Optional[List[Dict[str, Any]]] = self._bvit_setups(
                payload_config_row.bvit_pattern_id
            )
        else:
            bvit_setups = None

        instruments = {
            "salticam": salticam_setups,
            "rss": rss_setups,
            "hrs": hrs_setups,
            "bvit": bvit_setups,
        }

        return instruments

    def _salticam_setups(self, salticam_pattern_id: int) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT S.Salticam_Id AS salticam_id
FROM Salticam S
         JOIN SalticamPatternDetail SPD ON S.Salticam_Id = SPD.Salticam_Id
WHERE SPD.SalticamPattern_Id = :salticam_pattern_id
ORDER BY SPD.SalticamPattern_Order
        """
        )
        result = self.connection.execute(
            stmt, {"salticam_pattern_id": salticam_pattern_id}
        )
        return [
            self.instrument_repository.get_salticam(row.salticam_id) for row in result
        ]

    def _rss_setups(self, rss_pattern_id: int) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT R.Rss_Id AS rss_id
FROM Rss R
         JOIN RssPatternDetail RPD ON R.Rss_Id = RPD.Rss_Id
WHERE RPD.RssPattern_Id = :rss_pattern_id
ORDER BY RPD.RssPattern_Order
        """
        )
        result = self.connection.execute(stmt, {"rss_pattern_id": rss_pattern_id})
        return [self.instrument_repository.get_rss(row.rss_id) for row in result]

    def _hrs_setups(self, hrs_pattern_id: int) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT H.Hrs_Id AS hrs_id
FROM Hrs H
         JOIN HrsPatternDetail HPD ON H.Hrs_Id = HPD.Hrs_Id
WHERE HPD.HrsPattern_Id = :hrs_pattern_id
ORDER BY HPD.HrsPattern_Order
        """
        )
        result = self.connection.execute(stmt, {"hrs_pattern_id": hrs_pattern_id})
        return [self.instrument_repository.get_hrs(row.hrs_id) for row in result]

    def _bvit_setups(self, bvit_pattern_id: int) -> List[Dict[str, Any]]:
        stmt = text(
            """
SELECT B.Bvit_Id AS bvit_id
FROM Bvit B
         JOIN BvitPatternDetail BPD ON B.Bvit_Id = BPD.Bvit_Id
WHERE BPD.BvitPattern_Id = :bvit_pattern_id
ORDER BY BPD.BvitPattern_Order
        """
        )
        result = self.connection.execute(stmt, {"bvit_pattern_id": bvit_pattern_id})
        return [self.instrument_repository.get_bvit(row.bvit_id) for row in result]

    def _has_subblock_or_subsubblock_iterations(self, block_id: int) -> bool:
        """
        Check whether a block contains subblocks or subsubblocks with multiple
        iterations.
        """

        stmt = text(
            """
SELECT COUNT(*) AS c
FROM Pointing P
         JOIN SubBlock SB ON P.Block_Id = SB.Block_Id
         JOIN SubSubBlock SSB
              ON P.Block_Id = SSB.Block_Id AND P.SubBlock_Order = SSB.SubBlock_Order AND
                 P.SubSubBlock_Order = SSB.SubSubBlock_Order
         JOIN Block B ON P.Block_Id = B.Block_Id
WHERE B.Block_Id = :block_id
  AND (SB.Iterations > 1 OR SSB.Iterations > 1)
        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})
        return cast(bool, result.scalar_one() > 0)

    def _has_multiple_observations(self, pointing_id: int) -> bool:
        """
        Check whether a pointing contains multiple observations.
        """
        stmt = text(
            """
SELECT COUNT(DISTINCT Observation_Order) AS c
FROM TelescopeConfigObsConfig TCOC
WHERE TCOC.Pointing_Id = :pointing_id
        """
        )
        result = self.connection.execute(stmt, {"pointing_id": pointing_id})
        return cast(bool, result.scalar_one() > 1)
