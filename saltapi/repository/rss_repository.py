from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.service.instrument import RSS


class RssRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get(self, rss_id: int) -> RSS:
        stmt = text(
            """
SELECT R.Rss_Id                        AS rss_id,
       R.Iterations                    AS cycles,
       R.TotalExposureTime / 1000      AS observation_time,
       R.OverheadTime / 1000           AS overhead_time,
       RM.Mode                         AS mode,
       IF(RC.RssSpectroscopy_Id, 1, 0) AS has_spectroscopy,
       IF(RC.RssFabryPerot_Id, 1, 0)   AS has_fp,
       IF(RC.RssPolarimetry_Id, 1, 0)  AS has_polarimetry,
       IF(RC.RssMask_Id, 1, 0)            has_mask,
       IF(RMMD.RssMask_Id, 1, 0)       AS has_mos_mask,
       RG.Grating                      AS grating,
       RS.GratingAngle / 1000          AS grating_angle,
       RAS.Location                    AS articulation_station,
       RFPM.FabryPerot_Mode            AS fp_mode,
       RBSO.BeamSplitterOrientation       beam_splitter_orientation,
       RF.Barcode                      AS filter,
       RMT.RssMaskType                 AS mask_type,
       RMA.Barcode                     AS mask_barcode,
       RMMD.Equinox                    AS mos_equinox,
       RMMD.CutBy                      AS mos_cut_by,
       RMMD.CutDate                    AS mos_cut_date,
       RMMD.SaComment                  AS mos_comment
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
         LEFT JOIN RssMaskType RMT ON RMA.RssMaskType_Id = RMT.RssMaskType_Id
         LEFT JOIN RssMosMaskDetails RMMD ON RMA.RssMask_Id = RMMD.RssMask_Id
         JOIN RssProcedure RP ON R.RssProcedure_Id = RP.RssProcedure_Id
         JOIN RssDetector RD ON R.RssDetector_Id = RD.RssDetector_Id
WHERE R.Rss_Id = :rss_id
ORDER BY Rss_Id DESC;
        """
        )
        result = self.connection.execute(stmt, {"rss_id": rss_id})
        row = result.one()

        rss = {
            "id": row.rss_id,
            "name": "RSS",
            "cycles": row.cycles,
            "configuration": self._configuration(row),
            "observation_time": row.observation_time,
            "overhead_time": row.overhead_time,
        }
        return rss

    def _spectroscopy(self, row: Any) -> Optional[Dict[str, Any]]:
        """Return an RSS spectroscopy setup."""
        if not row.has_spectroscopy:
            return None

        camera_angle = row.articulation_station.split("_")[1]
        spectroscopy = {
            "grating": row.grating,
            "grating_angle": row.grating_angle,
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
            }
        else:
            mask = {
                "mask_type": row.mask_type,
                "barcode": row.mask_barcode,
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
