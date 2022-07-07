from sqlalchemy.engine import Connection

from saltapi.repository.finder_chart_repository import FinderChartRepository
from saltapi.service.finder_chart_service import FinderChartService


def test_get_finder_chart(db_connection: Connection) -> None:
    finding_chart_id = 55345
    proposal_code = "2015-2-SCI-028"

    repository = FinderChartRepository(db_connection)
    service = FinderChartService(repository)

    finding_chart = service.get_finder_chart(finding_chart_id)

    assert finding_chart[0] == proposal_code
