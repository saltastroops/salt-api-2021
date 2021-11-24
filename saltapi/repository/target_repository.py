from typing import Any, Dict, Optional

import pytz
from astropy.coordinates import Angle
from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.target import Target


class TargetRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, target_id: int) -> Target:
        stmt = text(
            """
SELECT T.Target_Id                          AS id,
       T.Target_Name                    AS name,
       TC.RaH                           AS ra_h,
       TC.RaM                           AS ra_m,
       TC.RaS                           AS ra_s,
       TC.DecSign                       AS dec_sign,
       TC.DecD                          AS dec_d,
       TC.DecM                          AS dec_m,
       TC.DecS                          AS dec_s,
       TC.Equinox                       AS equinox,
       TM.MinMag                        AS min_mag,
       TM.MaxMag                        AS max_mag,
       BP.FilterName                    AS bandpass,
       TST.TargetSubType                AS target_sub_type,
       TT.TargetType                    AS target_type,
       MT.RaDot                         AS ra_dot,
       MT.DecDot                        AS dec_dot,
       MT.Epoch                         AS epoch,
       PT.Period                        AS period,
       PT.Pdot                          AS period_change_rate,
       PT.T0                            AS period_zero_point,
       TB.Time_Base                     AS period_time_base,
       HT.Identifier                    AS horizons_identifier,
       IF(MT1.Target_Id IS NOT NULL,
          1,
          0)                            AS non_sidereal
FROM Target T
         LEFT JOIN TargetCoordinates TC
                   ON T.TargetCoordinates_Id = TC.TargetCoordinates_Id
         LEFT JOIN TargetMagnitudes TM ON T.TargetMagnitudes_Id = TM.TargetMagnitudes_Id
         LEFT JOIN Bandpass BP ON TM.Bandpass_Id = BP.Bandpass_Id
         LEFT JOIN TargetSubType TST ON T.TargetSubType_Id = TST.TargetSubType_Id
         LEFT JOIN TargetType TT ON TST.TargetType_Id = TT.TargetType_Id
         LEFT JOIN MovingTarget MT ON T.MovingTarget_Id = MT.MovingTarget_Id
         LEFT JOIN PeriodicTarget PT ON T.PeriodicTarget_Id = PT.PeriodicTarget_Id
         LEFT JOIN TimeBase TB ON PT.TimeBase_Id = TB.TimeBase_Id
         LEFT JOIN HorizonsTarget HT ON T.HorizonsTarget_Id = HT.HorizonsTarget_Id
         LEFT JOIN MovingTable MT1 ON T.Target_Id = MT1.Target_Id
WHERE T.Target_Id = :target_id;
        """
        )
        result = self.connection.execute(stmt, {"target_id": target_id})
        row = result.one()

        target = {
            "id": row.id,
            "name": row.name,
            "coordinates": self._coordinates(row),
            "proper_motion": self._proper_motion(row),
            "magnitude": self._magnitude(row),
            "target_type": self._target_type(row),
            "period_ephemeris": self._period_ephemeris(row),
            "horizons_identifier": row.horizons_identifier,
            "non_sidereal": row.non_sidereal > 0
        }

        return target

    @staticmethod
    def _coordinates(row: Any) -> Optional[Dict[str, Any]]:
        if row.ra_h is None:
            return None

        ra = Angle(f"{row.ra_h}:{row.ra_m}:{row.ra_s} hours").degree
        dec = Angle(f"{row.dec_sign}{row.dec_d}:{row.dec_m}:{row.dec_s} degrees").degree

        if ra == 0 and dec == 0:
            return None

        return {"right_ascension": ra, "declination": dec, "equinox": row.equinox}

    @staticmethod
    def _magnitude(row: Any) -> Optional[Dict[str, Any]]:
        if row.min_mag is None:
            return None

        return {
            "minimum_magnitude": row.min_mag,
            "maximum_magnitude": row.max_mag,
            "bandpass": row.bandpass,
        }

    @staticmethod
    def _proper_motion(row: Any) -> Optional[Dict[str, Any]]:
        if row.ra_dot is None or (row.ra_dot == 0 and row.dec_dot == 0):
            return None

        return {
            "right_ascension_speed": row.ra_dot,
            "declination_speed": row.dec_dot,
            "epoch": pytz.utc.localize(row.epoch),
        }

    @staticmethod
    def _target_type(row: Any) -> Optional[str]:
        if row.target_sub_type is None:
            return None

        if row.target_type != "Unknown":
            return f"{row.target_type} - {row.target_sub_type}"
        else:
            return "Unknown"

    @staticmethod
    def _period_ephemeris(row: Any) -> Optional[Dict[str, Any]]:
        if row.period is None:
            return None

        return {
            "zero_point": row.period_zero_point,
            "period": row.period,
            "period_change_rate": row.period_change_rate,
            "time_base": row.period_time_base,
        }
