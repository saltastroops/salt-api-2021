from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.instrument import RSS
from saltapi.util import semester_end, semester_of_datetime


class RssRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get(self, rss_id: int) -> RSS:
        stmt = text(
            """
SELECT R.Rss_Id                                          AS rss_id,
       R.Iterations                                      AS cycles,
       R.TotalExposureTime / 1000                        AS observation_time,
       R.OverheadTime / 1000                             AS overhead_time,
       RM.Mode                                           AS mode,
       IF(RC.RssSpectroscopy_Id IS NOT NULL, 1, 0)       AS has_spectroscopy,
       IF(RC.RssFabryPerot_Id IS NOT NULL, 1, 0)         AS has_fp,
       IF(RC.RssPolarimetry_Id IS NOT NULL, 1, 0)        AS has_polarimetry,
       IF(RC.RssMask_Id IS NOT NULL, 1, 0)               AS has_mask,
       IF(RMMD.RssMask_Id IS NOT NULL, 1, 0)             AS has_mos_mask,
       IF(RDW.RssDetectorWindow_Id IS NOT NULL, 1, 0)    AS has_detector_window,
       IF(RP.RssEtalonPattern_Id IS NOT NULL, 1, 0)      AS has_etalon_pattern,
       IF(RP.RssPolarimetryPattern_Id IS NOT NULL, 1, 0) AS has_polarimetry_pattern,
       RG.Grating                                        AS grating,
       RS.GratingAngle / 1000                            AS grating_angle,
       RAS.Location                                      AS articulation_station,
       RFPM.FabryPerot_Mode                              AS fp_mode,
       RBSO.BeamSplitterOrientation                      AS beam_splitter_orientation,
       RF.Barcode                                        AS filter,
       RMT.RssMaskType                                   AS mask_type,
       RMA.Barcode                                       AS mask_barcode,
       RPMD.Description                                  AS mask_description,
       RMMD.Equinox                                      AS mos_equinox,
       RMMD.CutBy                                        AS mos_cut_by,
       RMMD.CutDate                                      AS mos_cut_date,
       RMMD.SaComment                                    AS mos_comment,
       RDM.DetectorMode                                  AS detector_mode,
       RD.PreShuffle                                     AS pre_shuffle,
       RD.PostShuffle                                    AS post_shuffle,
       RD.PreBinRows                                     AS pre_binned_rows,
       RD.PreBinCols                                     AS pre_binned_cols,
       RD.ExposureTime / 1000                            AS exposure_time,
       RD.Iterations                                     AS detector_iterations,
       RET.ExposureType                                  AS exposure_type,
       G.Gain                                            AS gain,
       RRS.RoSpeed                                       AS readout_speed,
       RDC.Calculation                                   AS detector_calculation,
       RDW.Height                                        AS window_height,
       RPT.RssProcedureType                              AS procedure_type,
       RP.RssEtalonPattern_Id                            AS etalon_pattern_id,
       RP.RssPolarimetryPattern_Id                       AS polarimetry_pattern_id,
       RPP.PatternName                                   AS polarimetry_pattern_name
FROM Rss R
         JOIN RssConfig RC ON R.RssConfig_Id = RC.RssConfig_Id
         JOIN RssMode RM ON RC.RssMode_Id = RM.RssMode_Id
         LEFT JOIN RssSpectroscopy RS ON RC.RssSpectroscopy_Id = RS.RssSpectroscopy_Id
         LEFT JOIN RssGrating RG ON RS.RssGrating_Id = RG.RssGrating_Id
         LEFT JOIN RssArtStation RAS
                   ON RS.RssArtStation_Number = RAS.RssArtStation_Number
         LEFT JOIN RssFabryPerot RFP ON RC.RssFabryPerot_Id = RFP.RssFabryPerot_Id
         LEFT JOIN RssFabryPerotMode RFPM
                   ON RFP.RssFabryPerotMode_Id = RFPM.RssFabryPerotMode_Id
         LEFT JOIN RssPolarimetry RPO ON RC.RssPolarimetry_Id = RPO.RssPolarimetry_Id
         LEFT JOIN RssBeamSplitterOrientation RBSO
                   ON RPO.RssBeamSplitterOrientation_Id =
                      RBSO.RssBeamSplitterOrientation_Id
         JOIN RssFilter RF ON RC.RssFilter_Id = RF.RssFilter_Id
         LEFT JOIN RssMask RMA ON RC.RssMask_Id = RMA.RssMask_Id
         LEFT JOIN RssPredefinedMaskDetails RPMD ON RMA.RssMask_Id = RPMD.RssMask_Id
         LEFT JOIN RssMaskType RMT ON RMA.RssMaskType_Id = RMT.RssMaskType_Id
         LEFT JOIN RssMosMaskDetails RMMD ON RMA.RssMask_Id = RMMD.RssMask_Id
         JOIN RssProcedure RP ON R.RssProcedure_Id = RP.RssProcedure_Id
         JOIN RssProcedureType RPT ON RP.RssProcedureType_Id = RPT.RssProcedureType_Id
         JOIN RssDetector RD ON R.RssDetector_Id = RD.RssDetector_Id
         JOIN RssDetectorMode RDM ON RD.RssDetectorMode_Id = RDM.RssDetectorMode_Id
         JOIN RssExposureType RET ON RD.RssExposureType_Id = RET.RssExposureType_Id
         JOIN RssGain G ON RD.RssGain_Id = G.RssGain_Id
         JOIN RssRoSpeed RRS ON RD.RssRoSpeed_Id = RRS.RssRoSpeed_Id
         JOIN RssDetectorCalc RDC ON RD.RssDetectorCalc_Id = RDC.RssDetectorCalc_Id
         LEFT JOIN RssDetectorWindow RDW
                   ON RD.RssDetectorWindow_Id = RDW.RssDetectorWindow_Id
         LEFT JOIN RssPolarimetryPattern RPP
                   ON RP.RssPolarimetryPattern_Id = RPP.RssPolarimetryPattern_Id
WHERE R.Rss_Id = :rss_id
ORDER BY Rss_Id DESC;
        """
        )
        result = self.connection.execute(stmt, {"rss_id": rss_id})
        row = result.one()

        rss = {
            "id": row.rss_id,
            "configuration": self._configuration(row),
            "detector": self._detector(row),
            "procedure": self._procedure(row),
            "observation_time": row.observation_time,
            "overhead_time": row.overhead_time,
            "arc_bible_entries": self._arc_bible_entries(row),
        }
        return rss

    def _spectroscopy(self, row: Any) -> Optional[Dict[str, Any]]:
        """Return an RSS spectroscopy setup."""
        if not row.has_spectroscopy:
            return None

        camera_station, camera_angle = row.articulation_station.split("_")
        spectroscopy = {
            "grating": row.grating,
            "grating_angle": row.grating_angle,
            "camera_station": int(camera_station),
            "camera_angle": float(camera_angle),
        }
        return spectroscopy

    def _fabry_perot(self, row: Any) -> Optional[Dict[str, Any]]:
        """Return a Fabry-Perot setup."""
        if not row.has_fp:
            return None

        modes = {
            "HR": "High Resolution",
            "LR": "Low Resolution",
            "MR": "Medium Resolution",
            "TF": "Tunable Filter",
        }
        return {"mode": modes[row.fp_mode]}

    def _polarimetry(self, row: Any) -> Optional[Dict[str, Any]]:
        """Return a polarimetry setup."""
        if not row.has_polarimetry:
            return None

        return {"beam_splitter_orientation": row.beam_splitter_orientation}

    def _mask(self, row: Any) -> Optional[Dict[str, Any]]:
        if not row.has_mask:
            return None

        if not row.has_mos_mask:
            mask = {
                "mask_type": row.mask_type,
                "barcode": row.mask_barcode,
                "description": row.mask_description,
            }
        else:
            mask = {
                "mask_type": row.mask_type,
                "barcode": row.mask_barcode,
                "description": row.mask_description,
                "equinox": row.mos_equinox,
                "cut_by": row.mos_cut_by,
                "cut_date": row.mos_cut_date,
                "comment": row.mos_comment,
            }

        return mask

    def _configuration(self, row: Any) -> Dict[str, Any]:
        """Return an RSS configuration."""

        config = {
            "mode": row.mode,
            "spectroscopy": self._spectroscopy(row),
            "fabry_perot": self._fabry_perot(row),
            "polarimetry": self._polarimetry(row),
            "filter": row.filter,
            "mask": self._mask(row),
        }
        return config

    def _detector_calculation(self, row: Any) -> str:
        calculations = {
            "Focus": "Focus",
            "FPRingRadius": "FP Ring Radius",
            "MOS acquisition": "MOS Acquisition",
            "MOS mask calib": "MOS Mask Calibration",
            "MOS scan": "MOS Scan",
            "Nod & shuffle": "Nod & Shuffle",
            "None": "None",
        }
        return calculations[row.detector_calculation]

    def _detector(self, row: Any) -> Dict[str, Any]:
        """Return a RSS detector setup."""

        if row.has_detector_window:
            window: Optional[Dict[str, int]] = {"height": row.window_height}
        else:
            window = None

        detector = {
            "mode": row.detector_mode.title(),
            "pre_shuffled_rows": row.pre_shuffle,
            "post_shuffled_rows": row.post_shuffle,
            "pre_binned_rows": row.pre_binned_rows,
            "pre_binned_columns": row.pre_binned_cols,
            "exposure_time": row.exposure_time,
            "iterations": row.detector_iterations,
            "exposure_type": row.exposure_type,
            "gain": row.gain,
            "readout_speed": row.readout_speed,
            "detector_calculation": self._detector_calculation(row),
            "detector_window": window,
        }

        return detector

    def _procedure_type(self, row: Any) -> str:
        """Return the procedure type."""

        procedure_types = {
            "FABRY PEROT": "Fabry Perot",
            "FOCUS": "Focus",
            "FP CAL": "FP Cal",
            "FP POLARIMETRY": "FP Polarimetry",
            "FP RING": "FP Ring",
            "MOS ACQUISITION": "MOS Acquisition",
            "MOS CALIBRATION": "MOS Calibration",
            "MOS PEAKUP": "MOS Peakup",
            "NOD AND SHUFFLE": "Nod and Shuffle",
            "NORMAL": "Normal",
            "POLARIMETRY": "Polarimetry",
        }

        return procedure_types[row.procedure_type]

    def _etalon_wavelengths(self, etalon_pattern_id: int) -> List[float]:
        """
        Return the list of etalon wavelengths in an etalon pattern.
        """

        stmt = text(
            """
SELECT REPD.Wavelength / 1000 AS wavelength
FROM RssEtalonPatternDetail REPD
         JOIN RssEtalonPattern REP ON REPD.RssEtalonPattern_Id = REP.RssEtalonPattern_Id
WHERE REP.RssEtalonPattern_Id = :pattern_id
ORDER BY REPD.RssEtalonPattern_Order
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": etalon_pattern_id})

        return [row.wavelength for row in result]

    def _half_wave_plate_angles(self, polarimetry_pattern_id: int) -> Dict[int, float]:
        """
        Return a dictionary of orders (step numbers) and corresponding half-wave plate
        angles in a polarimetry pattern.
        """

        stmt = text(
            """
SELECT RHPD.RssHwPattern_Order AS `order`, RWS.RssWaveStation_Name AS station_name
FROM RssHwPatternDetail RHPD
         JOIN RssWaveStation RWS
              ON RHPD.RssWaveStation_Number = RWS.RssWaveStation_Number
         JOIN RssPolarimetryPattern RPP ON RHPD.RssHwPattern_Id = RPP.RssHwPattern_Id
WHERE RPP.RssPolarimetryPattern_Id = :pattern_id
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": polarimetry_pattern_id})

        return {row.order: row.station_name.split("_")[1] for row in result}

    def _quarter_wave_plate_angles(
        self, polarimetry_pattern_id: int
    ) -> Dict[int, float]:
        """
        Return a dictionary of order (step number) and corresponding quarter-wave
        plate angles in a polarimetry pattern.
        """

        stmt = text(
            """
SELECT RQPD.RssQwPattern_Order AS `order`, RWS.RssWaveStation_Name AS station_name
FROM RssQwPatternDetail RQPD
         JOIN RssWaveStation RWS
              ON RQPD.RssWaveStation_Number = RWS.RssWaveStation_Number
         JOIN RssPolarimetryPattern RPP ON RQPD.RssQwPattern_Id = RPP.RssQwPattern_Id
WHERE RPP.RssPolarimetryPattern_Id = :pattern_id
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": polarimetry_pattern_id})

        return {row.order: row.station_name.split("_")[1] for row in result}

    def _wave_plate_angles(
        self, polarimetry_pattern_id: int
    ) -> List[Dict[str, Optional[float]]]:
        """
        Return the sequence of half-wave plate and quarter-wave plate angles in a
        polarimetry pattern.
        """

        # Merge the orders may be used by the half-wave and the quarter-wave plate.
        half_angles = self._half_wave_plate_angles(polarimetry_pattern_id)
        quarter_angles = self._quarter_wave_plate_angles(polarimetry_pattern_id)
        orders_set = set(half_angles.keys()).union(quarter_angles.keys())

        # There should be at least one order.
        if len(orders_set) == 0:
            raise ValueError("No angles are defined for the polarimetry pattern.")

        # Collect the angles
        orders = list(orders_set)
        orders.sort()
        angles: List[Dict[str, Optional[float]]] = []
        for order in orders:
            angles.append(
                {
                    "half_wave": float(half_angles[order])
                    if order in half_angles
                    else None,
                    "quarter_wave": float(quarter_angles[order])
                    if order in quarter_angles
                    else None,
                }
            )

        return angles

    def _polarimetry_pattern(self, row: Any) -> Dict[str, Any]:
        """Return an RSS polarimetry pattern."""

        return {
            "name": row.polarimetry_pattern_name,
            "wave_plate_angles": self._wave_plate_angles(row.polarimetry_pattern_id),
        }

    def _procedure(self, row: Any) -> Dict[str, Any]:
        """Return an RSS procedure."""

        if row.has_etalon_pattern:
            etalon_wavelengths: Optional[List[float]] = self._etalon_wavelengths(
                row.etalon_pattern_id
            )
        else:
            etalon_wavelengths = None

        if row.has_polarimetry_pattern:
            polarimetry_pattern: Optional[Dict[str, Any]] = self._polarimetry_pattern(
                row
            )
        else:
            polarimetry_pattern = None

        return {
            "procedure_type": self._procedure_type(row),
            "cycles": row.cycles,
            "etalon_wavelengths": etalon_wavelengths,
            "polarimetry_pattern": polarimetry_pattern,
        }

    def _arc_bible_entries(self, row: Any) -> List[Dict[str, Any]]:
        """Return the arc bible entries."""

        stmt = text(
            """
SELECT L.Lamp                                     AS lamp,
       IF(AE.Lamp_Id = AB.PreferredLamp_Id, 1, 0) AS is_preferred_lamp,
       AE.OrigExptime                             AS original_exposure_time,
       arc_calculator(AE.Lamp_Id, AE.Exptime, SUBSTRING(RM.Barcode, 3, 4) / 100,
                      :binned_rows,
                      :binned_cols)               AS preferred_exposure_time
FROM ArcExposure AE
         JOIN Lamp L ON AE.Lamp_Id = L.Lamp_Id
         JOIN ArcBible AB ON AE.ArcBible_Id = AB.ArcBible_Id
         JOIN RssSpectroscopy RS ON AB.RssGrating_Id = RS.RssGrating_Id AND
                                    AB.RssArtStation_Number = RS.RssArtStation_Number
         JOIN RssConfig RC ON RS.RssSpectroscopy_Id = RC.RssSpectroscopy_Id
         JOIN RssMask RM ON RC.RssMask_Id = RM.RssMask_Id
         JOIN Rss R ON RC.RssConfig_Id = R.RssConfig_Id
WHERE R.Rss_Id = :rss_id
ORDER BY is_preferred_lamp DESC
        """
        )
        result = self.connection.execute(
            stmt,
            {
                "binned_rows": row.pre_binned_rows,
                "binned_cols": row.pre_binned_cols,
                "rss_id": row.rss_id,
            },
        )

        entries = [
            {
                "lamp": row.lamp,
                "is_preferred_lamp": True if row.is_preferred_lamp else False,
                "original_exposure_time": row.original_exposure_time,
                "preferred_exposure_time": row.preferred_exposure_time,
            }
            for row in result
        ]
        return entries

    def get_mask_in_magazine(self, mask_type: Optional[str] = None) -> List[str]:
        """
        The list of masks in the magazine, optionally filtered by a mask type.
        """
        stmt = """
SELECT
    Barcode AS barcode
FROM RssCurrentMasks AS RCM
    JOIN RssMask AS RM ON RCM.RssMask_Id = RM.RssMask_Id
    JOIN RssMaskType AS RMT ON RM.RssMaskType_Id = RMT.RssMaskType_Id
        """
        if mask_type:
            stmt += " WHERE RssMaskType = :mask_type"

        results = self.connection.execute(text(stmt), {"mask_type": mask_type})

        return [row.barcode for row in results]

    def _get_liaison_astronomers(self, proposal_code_ids: Set[int]) -> Dict[int, str]:
        stmt = text(
            """
        SELECT DISTINCT
            ProposalCode_Id AS proposal_code_id,
            Surname         AS surname
        FROM Proposal
            JOIN ProposalContact PCO USING (ProposalCode_Id)
            JOIN Investigator I ON (PCO.Astronomer_Id=I.Investigator_Id)
        WHERE ProposalCode_Id IN :proposal_code_ids
                """
        )
        results = self.connection.execute(
            stmt, {"proposal_code_ids": tuple(proposal_code_ids)}
        )
        liaison_astronomers = dict()
        for row in results:
            liaison_astronomers[row["proposal_code_id"]] = row["surname"]
        return liaison_astronomers

    def _get_barcodes_for_encoded_contents(
        self, encoded_contents: Set[str]
    ) -> Dict[Any, List[str]]:
        """
        Get the barcodes for a set of encoded mask contents.

        A dictionary of encoded contents and corresponding lists of barcodes is
        returned. If a list of barcodes has more than one item, this means that some
        masks have the same layout (slits, reference stars) but different barcodes.
        """
        stmt = text(
            """
SELECT
    EncodedContent 	AS encoded_content,
    Barcode 		AS barcode
FROM RssMosMaskDetails RMMD
    JOIN RssMask RM ON (RM.RssMask_Id = RMMD.RssMask_Id)
WHERE EncodedContent IN :encoded_contents
            """
        )
        ec = defaultdict(list)
        for row in self.connection.execute(
            stmt, {"encoded_contents": tuple(encoded_contents)}
        ):
            ec[row.encoded_content].append(row.barcode)
        return ec

    def _get_blocks_remaining_nights(self, block_ids: Set[int]) -> Dict[str, int]:

        stmt = text(
            """
SELECT B.Block_Id                                                         AS block_id,
       COUNT(DISTINCT DATE(DATE_SUB(BVW.VisibilityStart, INTERVAL 12 HOUR))) AS nights
FROM BlockVisibilityWindow BVW
         JOIN BlockVisibilityWindowType BVWT
         ON BVW.BlockVisibilityWindowType_Id = BVWT.BlockVisibilityWindowType_Id
         JOIN Block B ON BVW.Block_Id = B.Block_Id
WHERE BVW.VisibilityStart BETWEEN :start AND :end
  AND B.Block_Id IN :block_ids
  AND BVWT.BlockVisibilityWindowType='Strict'
GROUP BY B.Block_Id
            """
        )
        start = datetime.now()
        end = semester_end(semester_of_datetime(start.astimezone()))

        remaining_nights = dict()
        for n in self.connection.execute(
            stmt, {"block_ids": tuple(block_ids), "start": start, "end": end}
        ):
            remaining_nights[n.block_id] = n.nights
        return remaining_nights

    def get_mos_masks_metadata(
        self, from_semester: str, to_semester: str
    ) -> List[Dict[str, Any]]:

        stmt = text(
            """
SELECT DISTINCT
    P.Proposal_Id       AS proposal_id,
    Proposal_Code       AS proposal_code,
    PC.ProposalCode_Id  AS proposal_code_id,
    PI.Surname          AS pi_surname,
    BlockStatus         AS block_status,
    B.Block_Id          AS block_id,
    Block_Name          AS block_name,
    Priority            AS priority,
    NVisits             AS n_visits,
    NDone               AS n_done,
    Barcode             AS barcode,
    15.0 * RaH + 15.0 * RaM / 60.0 + 15.0 * RaS / 3600.0 AS ra_center,
    CutBy               AS cut_by,
    CutDate             AS cut_date,
    SaComment           AS mask_comment,
    EncodedContent      AS encoded_content
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
    AND CONCAT(S.Year, '-', S.Semester) >= :from_semester
    AND CONCAT(S.Year, '-', S.Semester) <= :to_semester
ORDER BY P.Semester_Id, Proposal_Code, Proposal_Id DESC
        """
        )
        results = self.connection.execute(
            stmt, {"from_semester": from_semester, "to_semester": to_semester}
        )

        mos_blocks = []
        block_ids = []
        encoded_contents = []
        for row in results:
            mos_blocks.append(dict(row, **{"other_barcodes": []}))
            block_ids.append(row.block_id)

            encoded_contents.append(row.encoded_content)
        proposal_code_ids = set([m["proposal_code_id"] for m in mos_blocks])
        if not proposal_code_ids:
            return []
        liaison_astronomers = self._get_liaison_astronomers(proposal_code_ids)
        barcodes = self._get_barcodes_for_encoded_contents(set(encoded_contents))
        remaining_nights = self._get_blocks_remaining_nights(set(block_ids))
        for m in mos_blocks:
            proposal_code_id = m["proposal_code_id"]
            liaison_astronomer = (
                liaison_astronomers[proposal_code_id]
                if proposal_code_id in liaison_astronomers
                else None
            )
            m["other_barcodes"] = [
                b for b in barcodes[m["encoded_content"]] if b != m["barcode"]
            ]
            m["remaining_nights"] = (
                remaining_nights[m["block_id"]]
                if m["block_id"] in remaining_nights
                else 0
            )
            m["liaison_astronomer"] = liaison_astronomer
        return mos_blocks

    def get_mos_mask_metadata(self, barcode: str) -> Dict[str, Any]:
        stmt = text(
            """
SELECT
    CutBy		AS cut_by,
    CutDate		AS cut_date,
    SaComment	AS mask_comment,
    Barcode		As barcode
FROM RssMosMaskDetails AS RMMD
    JOIN RssMask AS RM ON RMMD.RssMask_Id = RM.RssMask_Id
WHERE Barcode = :barcode
            """
        )
        result = self.connection.execute(stmt, {"barcode": barcode})
        row = result.one()
        return {**row}

    def update_mos_mask_metadata(
        self, mos_mask_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update MOS mask metadata"""
        stmt = text(
            """
UPDATE RssMosMaskDetails
SET CutBy = :cut_by, CutDate = :cut_date, saComment = :mask_comment
WHERE RssMask_Id = ( SELECT RssMask_Id FROM RssMask WHERE Barcode = :barcode )
    """
        )
        self.connection.execute(stmt, mos_mask_metadata)

        return self.get_mos_mask_metadata(mos_mask_metadata["barcode"])

    def get_obsolete_rss_masks_in_magazine(self, mask_type: Optional[str]) -> List[str]:
        """
        The list of obsolete RSS masks, optionally filtered by a mask type.
        """
        stmt = """
SELECT DISTINCT
    Barcode AS barcode
FROM Proposal P
    JOIN Semester S ON (P.Semester_Id=S.Semester_Id)
    JOIN Block B ON (P.Proposal_Id=B.Proposal_Id)
    JOIN BlockStatus BS ON (B.BlockStatus_Id=BS.BlockStatus_Id)
    JOIN Pointing PO USING (Block_Id)
    JOIN TelescopeConfigObsConfig USING (Pointing_Id)
    JOIN ObsConfig ON (PlannedObsConfig_Id=ObsConfig_Id)
    JOIN RssPatternDetail USING (RssPattern_Id)
    JOIN Rss USING (Rss_Id)
    JOIN RssConfig USING (RssConfig_Id)
    JOIN RssMask RM USING (RssMask_Id)
    JOIN RssMaskType USING (RssMaskType_Id)
WHERE CONCAT(S.Year, '-', S.Semester) >= :semester
    AND (BlockStatus = "Active" OR BlockStatus = "On Hold")
    AND NVisits >= NDone
"""
        if mask_type:
            stmt += " AND RssMaskType = :mask_type"
        needed_masks = [
            m["barcode"]
            for m in self.connection.execute(
                text(stmt),
                {
                    "semester": semester_of_datetime(datetime.now().astimezone()),
                    "mask_type": mask_type,
                },
            )
        ]

        obsolete_masks = []
        for m in self.get_mask_in_magazine(mask_type):
            if m not in needed_masks:
                obsolete_masks.append(m)
        return obsolete_masks
