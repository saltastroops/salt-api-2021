import pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.settings import Settings
from tests.conftest import (
    TEST_DATA,
    authenticate,
    not_authenticated,
    read_testdata,
)

PROPOSALS_URL = "/proposals"

USERS = read_testdata(TEST_DATA)
SECRET_KEY = Settings().secret_key


def test_should_return_401_for_get_proposals_for_unauthenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)
    response = client.get(PROPOSALS_URL + "/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "user_type",
    [
        "investigators",
        "principal_investigators",
        "administrator",
        "salt_astronomer",
        "tac_members",
        "tac_chairs",
    ],
)
def test_should_return_list_of_proposals_for_get_proposals_for_authenticated_users(
    user_type: str, client: TestClient
) -> None:
    username = ""
    if user_type == "investigators" or user_type == "principal_investigators":
        username = USERS[user_type]["2019-2-SCI-006"]
    elif user_type == "administrator" or user_type == "salt_astronomer":
        username = USERS[user_type]
    else:
        username = USERS[user_type]["RSA"]

    authenticate(username, client)
    response = client.get(PROPOSALS_URL + "/")
    assert response.status_code == status.HTTP_200_OK
    assert "proposal_code" in [p for proposal in response.json() for p in proposal]
    assert "semester" in [p for proposal in response.json() for p in proposal]
    assert "principal_investigator" in [p for proposal in response.json() for p in proposal]


@pytest.mark.parametrize(
    "from_semester, to_semester",
    [
        ("2022-1", "2021-2"),
        ("2020-1", "2019-2"),
        ("2022-2", "2020-1"),
    ],
)
def test_should_return_400_if_start_semester_not_less_than_end_semester(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = USERS["administrator"]
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "from_semester, to_semester",
    [
        ("abc", "2021-2"),
        ("2", "2019-2"),
        ("2022", "2020-1"),
        ("2020-1", "2021-3"),
        ("2020-1", "abc"),
    ],
)
def test_should_return_422_for_invalid_semesters(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = USERS["administrator"]
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "limit",
    [
        0,
        30,
        102,
    ],
)
def test_should_return_200_for_get_limited_proposals(
    limit: int, client: TestClient
) -> None:
    username = USERS["administrator"]
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={"limit": limit},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == limit


def test_should_return_422_for_invalid_limit(client: TestClient) -> None:
    username = USERS["administrator"]
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={"limit": -1},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_should_return_1000_for_get_proposals_for_default_limit(
    client: TestClient,
) -> None:
    username = USERS["administrator"]
    authenticate(username, client)
    response = client.get(PROPOSALS_URL + "/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1000
