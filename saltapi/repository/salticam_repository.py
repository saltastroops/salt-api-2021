from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.instrument import Salticam


class SalticamRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get(self, salticam_id: int) -> Salticam:
        """Return a Salticam setup."""

        stmt = text(
            """
SELECT S.Salticam_Id                                     AS salticam_id,
       S.Iterations                                      AS cycles,
       IF(S.SalticamDetector_Id IS NOT NULL, 1, 0)       AS has_detector,
       IF(S.SalticamProcedure_Id IS NOT NULL, 1, 0)      AS has_procedure,
       IF(SD.SalticamWindowPattern_Id IS NOT NULL, 1, 0) AS has_detector_windows,
       SDM.XmlDetectorMode                               AS detector_mode,
       SD.PreBinRows                                     AS pre_binned_rows,
       SD.PreBinCols                                     AS pre_binned_cols,
       SD.Iterations                                     AS detector_iterations,
       SETY.ExposureType                                 AS exposure_type,
       SG.Gain                                           AS gain,
       SRS.RoSpeed                                       AS readout_speed,
       SD.SalticamWindowPattern_Id                       AS window_pattern_id,
       SP.SalticamFilterPattern_Id                       AS filter_pattern_id,
       S.MinSN                                           AS minimum_signal_to_noise,
       S.ObservingTime / 1000                            AS observation_time,
       S.OverheadTime / 1000                             AS overhead_time
FROM Salticam S
         LEFT JOIN SalticamDetector SD ON S.SalticamDetector_Id = SD.SalticamDetector_Id
         LEFT JOIN SalticamDetectorMode SDM
                   ON SD.SalticamDetectorMode_Id = SDM.SalticamDetectorMode_Id
         LEFT JOIN SalticamExposureType SETY
                   ON SD.SalticamExposureType_Id = SETY.SalticamExposureType_Id
         LEFT JOIN SalticamGain SG ON SD.SalticamGain_Id = SG.SalticamGain_Id
         LEFT JOIN SalticamRoSpeed SRS ON SD.SalticamRoSpeed_Id = SRS.SalticamRoSpeed_Id
         LEFT JOIN SalticamProcedure SP
                   ON S.SalticamProcedure_Id = SP.SalticamProcedure_Id
WHERE S.Salticam_Id = :salticam_id
        """
        )
        result = self.connection.execute(stmt, {"salticam_id": salticam_id})
        row = result.one()

        if row.has_detector:
            detector: Optional[Dict[str, Any]] = self._detector(row)
        else:
            detector = None

        if row.has_procedure:
            procedure: Optional[Dict[str, Any]] = self._procedure(row)
        else:
            procedure = None

        salticam = {
            "id": row.salticam_id,
            "name": "Salticam",
            "cycles": row.cycles,
            "detector": detector,
            "procedure": procedure,
            "minimum_signal_to_noise": row.minimum_signal_to_noise,
            "observation_time": float(row.observation_time),
            "overhead_time": float(row.overhead_time),
        }

        return salticam

    def _detector_windows(self, window_pattern_id: int) -> List[Dict[str, Any]]:
        """Return Salticam detector windows."""

        stmt = text(
            """
SELECT SW.CentreRa  AS centre_ra,
       SW.CentreDec AS centre_dec,
       SW.Height    AS height,
       SW.Width     AS width
FROM SalticamWindow SW
WHERE SW.SalticamWindowPattern_Id = :pattern_id
ORDER BY SW.SalticamWindow_Order
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": window_pattern_id})

        # Dividing ra_centre and dec_centre in the SELECT query would introduce
        # inaccuracies.
        return [
            {
                "center_right_ascension": row.centre_ra / 3600.0,
                "center_declination": float(row.centre_dec) / 3600.0,
                "height": row.height,
                "width": row.width,
            }
            for row in result
        ]

    def _detector(self, row: Any) -> Dict[str, Any]:
        """Return a Salticam detector setup."""

        if row.has_detector_windows:
            windows: Optional[List[Dict[str, Any]]] = self._detector_windows(
                row.window_pattern_id
            )
        else:
            windows = None

        detector = {
            "mode": row.detector_mode,
            "pre_binned_rows": row.pre_binned_rows,
            "pre_binned_columns": row.pre_binned_cols,
            "iterations": row.detector_iterations,
            "exposure_type": row.exposure_type,
            "gain": row.gain,
            "readout_speed": row.readout_speed,
            "detector_windows": windows,
        }

        return detector

    def _exposures(self, filter_pattern_id: int) -> List[Dict[str, Any]]:
        """Return Salticam exposures."""

        stmt = text(
            """
SELECT SF.SalticamFilter_Name   AS filter_name,
       SF.DescriptiveName       AS filter_description,
       SFPD.ExposureTime / 1000 AS exposure_time
FROM SalticamFilterPatternDetail SFPD
         JOIN SalticamFilter SF ON SFPD.SalticamFilter_Id = SF.SalticamFilter_Id
WHERE SFPD.SalticamFilterPattern_Id = :pattern_id;
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": filter_pattern_id})

        return [
            {
                "filter": {
                    "name": row.filter_name,
                    "description": row.filter_description,
                },
                "exposure_time": row.exposure_time,
            }
            for row in result
        ]

    def _procedure(self, row: Any) -> Dict[str, Any]:
        """Return a Salticam procedure."""

        procedure = {"exposures": self._exposures(row.filter_pattern_id)}

        return procedure
