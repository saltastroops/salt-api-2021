from pathlib import Path
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError


class FinderChartRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, finder_chart_id: int) -> Tuple[str, Path]:
        stmt = text(
            """
SELECT DISTINCT PC.Proposal_code AS proposal_code,
                FC.Path AS finding_chart_path
FROM FindingChart FC
     JOIN Pointing P ON FC.Pointing_Id = P.Pointing_Id
     JOIN Block B ON P.Block_Id = B.Block_Id
     JOIN ProposalCode PC ON B.ProposalCode_Id = PC.ProposalCode_Id
WHERE FC.FindingChart_Id = :finder_chart_id
        """
        )
        try:
            result = self.connection.execute(stmt, {"finder_chart_id": finder_chart_id})

            finding_chart_details = result.one()
            return finding_chart_details[0], Path(finding_chart_details[1])
        except NoResultFound:
            raise NotFoundError(f"Unknown finder chart id: {finder_chart_id}")
