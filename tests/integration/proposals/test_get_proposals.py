import pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.settings import Settings
from tests.conftest import read_testdata, TEST_DATA, authenticate, not_authenticated

PROPOSALS_URL = "/proposals"

USERS = read_testdata(TEST_DATA)
SECRET_KEY = Settings().secret_key


# Unauthenticated users cannot request a proposal
def test_get_proposals_for_nonpermitted_user(client: TestClient) -> None:
    response = client.get(
        PROPOSALS_URL + "/", params={"user": not_authenticated(client)}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Get list of proposals
@pytest.mark.parametrize(
    "user_type",
    [
        "investigators",
        "principal_investigators",
        "principal_contacts",
    ],
)
def test_get_proposals_for_permitted_users(user_type, client: TestClient) -> None:
    data = USERS[user_type]
    usernames = data.values()
    for username in usernames:
        response = client.get(
            PROPOSALS_URL + "/",
            params={
                "user": authenticate(username, client),
            },
        )
        assert response.status_code == status.HTTP_200_OK


# The start of the semester must be less than or equal to the end semester
@pytest.mark.parametrize(
    "from_semester, to_semester",
    [
        ("2022-1", "2021-2"),
        ("2020-1", "2019-2"),
        ("2022-2", "2020-1"),
    ],
)
def test_start_semester_not_less_than_end_semester(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = USERS["administrator"]
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "user": authenticate(username, client),
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Invalid semesters are rejected
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
def test_invalid_semesters(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = USERS["administrator"]
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "user": authenticate(username, client),
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Get list of up to <limit> proposals
@pytest.mark.parametrize(
    "limit",
    [
        0,
        30,
        102,
    ],
)
def test_get_limited_proposals(limit: int, client: TestClient) -> None:
    username = USERS["administrator"]
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "user": authenticate(username, client),
            "limit": limit,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == limit


# A negative value is rejected for the maximum number of results
def test_invalid_limit(client: TestClient) -> None:
    username = USERS["administrator"]
    response = client.get(
        PROPOSALS_URL + "/",
        params={"user": authenticate(username, client), "limit": -1},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
