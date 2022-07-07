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


def test_get_finder_chart_returns_403_for_non_permitted_user(
    client: TestClient,
) -> None:
    authenticate("TestUser", client)
    response = client.get(FINDER_CHART_URL + "/" + str(1))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_returns_finder_chart_for_permitted_user(client: TestClient) -> None:
    authenticate(USERNAME, client)
    response = client.get(FINDER_CHART_URL + "/" + str(55345))

    assert response.status_code == status.HTTP_200_OK
    assert response.content.__sizeof__() > 0


def test_get_finder_chart_returns_404_for_wrong_finding_chart_id(
    client: TestClient,
) -> None:
    authenticate(USERNAME, client)
    finder_chart_id = 0

    response = client.get(FINDER_CHART_URL + "/" + str(finder_chart_id))

    assert response.status_code == status.HTTP_404_NOT_FOUND
