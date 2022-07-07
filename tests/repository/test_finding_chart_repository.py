import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.finding_chart_repository import FindingChartRepository


def test_get_finding_chart_returns_content(db_connection: Connection) -> None:
    finding_chart_id = 55345
    proposal_code = "2015-2-SCI-028"
    finding_chart_repository = FindingChartRepository(db_connection)
    finding_chart = finding_chart_repository.get(finding_chart_id)
    # assert type(finding_chart) == "str"
    assert finding_chart[0] == proposal_code
    assert "FindingChart" in finding_chart[1]


def test_raises_an_error_for_non_existing_finder_chart(
    db_connection: Connection,
) -> None:
    finding_chart_id = 0
    finding_chart_repository = FindingChartRepository(db_connection)

    with pytest.raises(ValueError) as excinfo:
        finding_chart_repository.get(finding_chart_id)

    assert str(finding_chart_id) in str(excinfo.value)
