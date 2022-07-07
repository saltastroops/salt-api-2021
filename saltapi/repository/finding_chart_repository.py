from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError
from saltapi.service.proposal import ProposalCode


class FindingChartRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get(self, finding_chart_id: int) -> Any:
        stmt = text(
            """
SELECT FC.Path AS finding_chart_path
FROM FindingChart FC
WHERE FC.FindingChart_Id = :finding_chart_id
        """
        )
        try:
            result = self.connection.execute(
                stmt, {"finding_chart_id": finding_chart_id}
            )
            proposal_code = self.get_proposal_code_for_finding_chart_id(
                finding_chart_id
            )
            finding_chart_path = result.one()
            return [proposal_code, finding_chart_path[0]]
        except NoResultFound:
            raise NotFoundError()

    def get_proposal_code_for_finding_chart_id(
        self, finding_chart_id: int
    ) -> ProposalCode:
        """
        Return proposal code for a finding chart id:
        """
        stmt = text(
            """
SELECT PC.Proposal_code
FROM ProposalCode PC
     JOIN Block B ON PC.ProposalCode_Id = B.ProposalCode_Id
     JOIN Pointing P ON B.Block_Id = P.Block_Id
     JOIN FindingChart FC ON P.Pointing_Id = FC.Pointing_Id
WHERE FC.FindingChart_Id = :finding_chart_id;
        """
        )
        result = self.connection.execute(
            stmt,
            {"finding_chart_id": finding_chart_id},
        )

        try:
            proposal_codes = result.fetchall()

            if len(proposal_codes) > 0:
                proposal_codes = [codes[0] for codes in proposal_codes]
                return cast(ProposalCode, list(set(proposal_codes))[0])
            else:
                raise NotFoundError(f"Unknown block visit id: {finding_chart_id}")
        except NoResultFound:
            raise NotFoundError()
