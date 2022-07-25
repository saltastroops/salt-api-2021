from sqlalchemy import text
from sqlalchemy.engine.base import Connection

from saltapi.service.instrument import BVIT


class BvitRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, bvit_id: int) -> BVIT:
        stmt = text(
            """
SELECT B.Bvit_Id                      AS bvit_id,
       BM.BvitMode                    AS mode,
       BF.BvitFilter_Name             AS filter,
       BND.BvitNeutralDensity_Setting AS neutral_density,
       B.IrisSize                     AS iris_size,
       B.ShutterOpenTime              AS shutter_open_time
FROM Bvit B
         JOIN BvitMode BM ON B.BvitMode_Id = BM.BvitMode_Id
         JOIN BvitFilter BF ON B.BvitFilter_Id = BF.BvitFilter_Id
         JOIN BvitNeutralDensity BND
              ON B.BvitNeutralDensity_Id = BND.BvitNeutralDensity_Id
WHERE B.Bvit_Id = :bvit_id;
        """
        )
        result = self.connection.execute(stmt, {"bvit_id": bvit_id})
        row = result.one()

        bvit = {
            "id": row.bvit_id,
            "mode": row.mode,
            "filter": row.filter,
            "neutral_density": row.neutral_density,
            "iris_size": row.iris_size,
            "shutter_open_time": row.shutter_open_time,
        }

        return bvit
