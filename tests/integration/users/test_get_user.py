from typing import Callable, Any

import pytest as pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, find_username, misauthenticate, not_authenticated


TEST_DATA = "integration/users/get_user.yaml"

USERS_URL = "/users/"


def _url(username: str) -> str:
    return USERS_URL + username


def test_get_user_should_return_401_for_unauthenticated_user(client: TestClient) -> None:
    not_authenticated(client)

    response = client.get(_url("hettlage"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_should_return_401_for_user_with_invalid_auth_token(client: TestClient) -> None:
    misauthenticate(client)

    response = client.get(_url("hettlage"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_should_return_404_for_non_existing_user(client: TestClient) -> None:
    authenticate(find_username("Administrator"), client)

    response = client.get(_url("idontexist"))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        find_username("Board Member"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("SALT Astronomer"),
    ],
)
def test_get_user_should_return_403_if_non_admin_tries_to_get_other_user(username: str, client: TestClient) -> None:
    other_username = find_username(
        "Principal Investigator", proposal_code="2020-2-DDT-005"
    )
    authenticate(username, client)

    response = client.get(_url(other_username))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_should_not_return_a_password(client: TestClient) -> None:
    username = find_username(
        "Principal Investigator", proposal_code="2020-2-DDT-005"
    )
    authenticate(username, client)

    response = client.get(_url(username))
    assert response.status_code == status.HTTP_200_OK
    for key in response.json().keys():
        assert "password" not in key.lower()


@pytest.mark.parametrize('username', [find_username("SALT Astronomer")])
def test_get_user_should_return_correct_user_details(username: str, client: TestClient, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)[username]

    authenticate(username, client)

    response = client.get(_url(username))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == data


def test_get_user_should_allow_admin_to_get_other_user(client: TestClient) -> None:
    username = find_username("Administrator")
    authenticate(username, client)

    other_username = find_username(
        "Principal Investigator", proposal_code="2020-2-DDT-005"
    )

    response = client.get(_url(other_username))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == other_username
