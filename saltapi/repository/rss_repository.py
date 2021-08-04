from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.instrument import RSS


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
       IF(RC.RssMask_Id IS NOT NULL, 1, 0)                  has_mask,
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
