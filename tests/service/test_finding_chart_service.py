from sqlalchemy.engine import Connection

from saltapi.repository.finding_chart_repository import FindingChartRepository
from saltapi.service.finding_chart_service import FindingChartService


def test_get_finder_chart(db_connection: Connection) -> None:
    finding_chart_id = 55345
    proposal_code = "2015-2-SCI-028"

    repository = FindingChartRepository(db_connection)
    service = FindingChartService(repository)

    finding_chart = service.get_finding_chart(finding_chart_id)

    assert finding_chart[0] == proposal_code
