import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.finder_chart_repository import FinderChartRepository


def test_get_finding_chart_returns_correct_content(db_connection: Connection) -> None:
    finding_chart_id = 55345
    proposal_code = "2015-2-SCI-028"
    expected_finder_chart_path = "4/Included/FindingChart_1445723219288.pdf"

    finding_chart_repository = FinderChartRepository(db_connection)
    finding_chart = finding_chart_repository.get(finding_chart_id)

    assert finding_chart[0] == proposal_code
    assert expected_finder_chart_path == str(finding_chart[1])


def test_raises_an_error_for_non_existing_finder_chart(
    db_connection: Connection,
) -> None:
    finder_chart_id = 0
    finder_chart_repository = FinderChartRepository(db_connection)

    with pytest.raises(ValueError) as excinfo:
        finder_chart_repository.get(finder_chart_id)

    assert str(finder_chart_id) in str(excinfo.value)
