from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.engine.base import Connection

from saltapi.service.instrument import HRS


class HrsRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, hrs_id: int) -> HRS:
        """Return an HRS setup."""

        stmt = text(
            """
SELECT H.Hrs_Id                                     AS hrs_id,
       H.ObservingTime / 1000                       AS observation_time,
       H.OverheadTime / 1000                        AS overhead_time,
       IF(HC.HrsNodAndShuffle_Id IS NOT NULL, 1, 0) AS has_nod_and_shuffle,
       HM.ExposureMode                              AS mode,
       HET.ExposureType                             AS exposure_type,
       HTL.TargetLocation                           AS target_location,
       HC.FibreSeparation                           AS fiber_separation,
       HICP.IodineCellPosition                      AS iodine_cell_position,
       ThArLampOn                                   AS th_ar_lamp_on,
       HNAS.NodInterval                             AS nod_interval,
       HNAS.NodCount                                AS nod_count,
       HBlueD.PreShuffle                            AS blue_pre_shuffle_rows,
       HBlueD.PostShuffle                           AS blue_post_shuffle_rows,
       HBlueD.PreBinRows                            AS blue_pre_binned_rows,
       HBlueD.PreBinCols                            AS blue_pre_binned_columns,
       HBlueD.Iterations                            AS blue_detector_iterations,
       HBlueS.RoSpeed                               AS blue_readout_speed,
       HBlueA.HrsRoAmplifiers                       AS blue_readout_amplifiers,
       HRedD.PreShuffle                             AS red_pre_shuffle_rows,
       HRedD.PostShuffle                            AS red_post_shuffle_rows,
       HRedD.PreBinRows                             AS red_pre_binned_rows,
       HRedD.PreBinCols                             AS red_pre_binned_columns,
       HRedD.Iterations                             AS red_detector_iterations,
       HRedS.RoSpeed                                AS red_readout_speed,
       HRedA.HrsRoAmplifiers                        AS red_readout_amplifiers,
       HP.Iterations                                AS cycles,
       HP.HrsBlueExposurePattern_Id                 AS blue_exposure_pattern_id,
       HP.HrsRedExposurePattern_Id                  AS red_exposure_pattern_id
FROM Hrs H
         JOIN HrsConfig HC ON H.HrsConfig_Id = HC.HrsConfig_Id
         JOIN HrsMode HM ON HC.HrsMode_Id = HM.HrsMode_Id
         JOIN HrsExposureType HET ON HC.HrsExposureType_Id = HET.HrsExposureType_Id
         JOIN HrsTargetLocation HTL
              ON HC.HrsTargetLocation_Id = HTL.HrsTargetLocation_Id
         JOIN HrsIodineCellPosition HICP
              ON HC.HrsIodineCellPosition_Id = HICP.HrsIodineCellPosition_Id
         LEFT JOIN HrsNodAndShuffle HNAS
                   ON HC.HrsNodAndShuffle_Id = HNAS.HrsNodAndShuffle_Id
         JOIN HrsBlueDetector HBlueD ON H.HrsBlueDetector_Id = HBlueD.HrsBlueDetector_Id
         JOIN HrsRoSpeed HBlueS ON HBlueD.HrsRoSpeed_Id = HBlueS.HrsRoSpeed_Id
         JOIN HrsRoAmplifiers HBlueA
              ON HBlueD.HrsRoAmplifiers_Id = HBlueA.HrsRoAmplifiers_Id
         JOIN HrsRedDetector HRedD ON H.HrsRedDetector_Id = HRedD.HrsRedDetector_Id
         JOIN HrsRoSpeed HRedS ON HRedD.HrsRoSpeed_Id = HRedS.HrsRoSpeed_Id
         JOIN HrsRoAmplifiers HRedA
              ON HRedD.HrsRoAmplifiers_Id = HRedA.HrsRoAmplifiers_Id
         JOIN HrsProcedure HP ON H.HrsProcedure_Id = HP.HrsProcedure_Id
WHERE H.Hrs_Id = :hrs_id
        """
        )
        result = self.connection.execute(stmt, {"hrs_id": hrs_id})
        row = result.one()

        hrs = {
            "id": hrs_id,
            "configuration": self._configuration(row),
            "blue_detector": self._blue_detector(row),
            "red_detector": self._red_detector(row),
            "procedure": self._procedure(row),
            "observation_time": row.observation_time,
            "overhead_time": row.overhead_time,
        }

        return hrs

    def _mode(self, row: Any) -> str:
        modes = {
            "HIGH RESOLUTION": "High Resolution",
            "HIGH STABILITY": "High Stability",
            "INT CAL FIBRE": "Int Cal Fiber",
            "LOW RESOLUTION": "Low Resolution",
            "MEDIUM RESOLUTION": "Medium Resolution",
        }

        return modes[row.mode]

    def _target_location(self, row: Any) -> str:
        locations = {
            "-1 ALPHA (STAR)": "The star fiber is placed on the optical axis",
            "0 (BISECT)": "The star and sky fiber are equidistant from the optical "
            "axis",
            "+1 ALPHA (SKY)": "The sky fiber is placed on the optical axis",
        }

        return locations[row.target_location]

    def _iodine_cell_position(self, row: Any) -> str:
        locations = {
            "Calibration": "Calibration",
            "IN": "In",
            "OUT": "Out",
            "ThAr in sky (O) fiber": "ThAr in sky fiber",
            "ThAr in star (P) fiber": "ThAr in star fiber",
        }

        return locations[row.iodine_cell_position]

    def _configuration(self, row: Any) -> Dict[str, Any]:
        """HRS configuration."""

        if row.has_nod_and_shuffle:
            nod_and_shuffle: Optional[Dict[str, int]] = {
                "nod_interval": row.nod_interval,
                "nod_count": row.nod_count,
            }
        else:
            nod_and_shuffle = None

        configuration = {
            "mode": self._mode(row),
            "exposure_type": row.exposure_type,
            "target_location": self._target_location(row),
            "fiber_separation": row.fiber_separation,
            "iodine_cell_position": self._iodine_cell_position(row),
            "is_th_ar_lamp_on": True if row.th_ar_lamp_on else False,
            "nod_and_shuffle": nod_and_shuffle,
        }

        return configuration

    def _blue_readout_amplifiers(self, row: Any) -> int:
        amplifiers = {"One": 1, "Multiple": 2}

        return amplifiers[row.blue_readout_amplifiers]

    def _blue_detector(self, row: Any) -> Dict[str, Any]:
        detector = {
            "pre_shuffled_rows": row.blue_pre_shuffle_rows,
            "post_shuffled_rows": row.blue_post_shuffle_rows,
            "pre_binned_rows": row.blue_pre_binned_rows,
            "pre_binned_columns": row.blue_pre_binned_columns,
            "iterations": row.blue_detector_iterations,
            "readout_speed": row.blue_readout_speed,
            "readout_amplifiers": self._blue_readout_amplifiers(row),
        }

        return detector

    def _red_readout_amplifiers(self, row: Any) -> int:
        amplifiers = {"One": 1, "Multiple": 4}

        return amplifiers[row.red_readout_amplifiers]

    def _red_detector(self, row: Any) -> Dict[str, Any]:
        detector = {
            "pre_shuffled_rows": row.red_pre_shuffle_rows,
            "post_shuffled_rows": row.red_post_shuffle_rows,
            "pre_binned_rows": row.red_pre_binned_rows,
            "pre_binned_columns": row.red_pre_binned_columns,
            "iterations": row.red_detector_iterations,
            "readout_speed": row.red_readout_speed,
            "readout_amplifiers": self._red_readout_amplifiers(row),
        }

        return detector

    def _procedure(self, row: Any) -> Dict[str, Any]:
        # Get the blue and red exposure times
        blue_pattern = self._exposure_pattern(row.blue_exposure_pattern_id)
        red_pattern = self._exposure_pattern(row.red_exposure_pattern_id)
        orders_set = set(blue_pattern.keys()).union(red_pattern.keys())
        if len(orders_set) == 0:
            raise ValueError(
                "Neither the blue nor the red exposure time pattern "
                "contains an exposure time."
            )
        orders = list(orders_set)
        orders.sort()
        blue_exposure_times = [blue_pattern.get(order) for order in orders]
        red_exposure_times = [red_pattern.get(order) for order in orders]

        procedure = {
            "cycles": row.cycles,
            "blue_exposure_times": blue_exposure_times,
            "red_exposure_times": red_exposure_times,
        }

        return procedure

    def _exposure_pattern(self, pattern_id: int) -> Dict[int, Decimal]:
        stmt = text(
            """
SELECT HEPD.HrsExposurePattern_Order AS step, HEPD.ExposureTime AS exposure_time
FROM HrsExposurePatternDetail HEPD
WHERE HEPD.HrsExposurePattern_Id = :pattern_id
        """
        )
        result = self.connection.execute(stmt, {"pattern_id": pattern_id})

        return {row.step: row.exposure_time for row in result}
