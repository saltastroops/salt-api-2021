from sqlalchemy.engine import Connection

from saltapi.repository.finder_chart_repository import FinderChartRepository
from saltapi.service.finder_chart_service import FinderChartService


def test_get_finder_chart(db_connection: Connection) -> None:
    finding_chart_id = 55345
    expected_proposal_code = "2015-2-SCI-028"
    expected_finder_chart_path = (
        expected_proposal_code + "/4/Included/FindingChart_1445723219288.pdf"
    )

    repository = FinderChartRepository(db_connection)
    service = FinderChartService(repository)

    proposal_code, finding_chart_path = service.get_finder_chart(finding_chart_id)

    assert expected_proposal_code == proposal_code
    assert expected_finder_chart_path in str(finding_chart_path)
