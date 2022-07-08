from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, not_authenticated

FINDER_CHART_URL = "/finder-charts"

USERNAME = "cmofokeng"


def test_get_finder_chart_returns_401_for_non_authenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)
    response = client.get(FINDER_CHART_URL + "/" + str(1))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_finder_chart_returns_403_for_non_authorised_user(
    client: TestClient,
) -> None:
    authenticate("TestUser", client)
    response = client.get(FINDER_CHART_URL + "/" + str(1))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_returns_finder_chart_for_authorised_user(client: TestClient) -> None:
    finder_chart_id = 55345
    proposal_code = "2015-2-SCI-028"
    expected_finder_chart_path = (
        proposal_code + "/4/Included/FindingChart_1445723219288.pdf"
    )
    authenticate(USERNAME, client)

    try:
        response = client.get(FINDER_CHART_URL + "/" + str(finder_chart_id))

        assert response.status_code == status.HTTP_200_OK
        assert response.content.__sizeof__() > 0
    except RuntimeError as excinfo:
        assert expected_finder_chart_path in excinfo.__str__()


def test_get_finder_chart_returns_404_for_wrong_finding_chart_id(
    client: TestClient,
) -> None:
    authenticate(USERNAME, client)
    finder_chart_id = 0

    response = client.get(FINDER_CHART_URL + "/" + str(finder_chart_id))

    assert response.status_code == status.HTTP_404_NOT_FOUND
