from typing import Any, Callable

import pytest as pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import (
    authenticate,
    find_username,
    get_authenticated_user_id,
    misauthenticate,
    not_authenticated,
)

TEST_DATA = "integration/users/get_user.yaml"

USERS_URL = "/users/"


def _url(user_id: int) -> str:
    return USERS_URL + str(user_id)


def test_get_user_should_return_401_for_unauthenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)
    user_id = 1
    response = client.get(_url(user_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_should_return_401_for_user_with_invalid_auth_token(
    client: TestClient,
) -> None:
    misauthenticate(client)
    user_id = 2
    response = client.get(_url(user_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_should_return_404_for_non_existing_user(client: TestClient) -> None:
    authenticate(find_username("Administrator"), client)

    response = client.get(_url(0))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        find_username("Board Member"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("SALT Astronomer"),
    ],
)
def test_get_user_should_return_403_if_non_admin_tries_to_get_other_user(
    username: str, client: TestClient
) -> None:
    other_user_id = 1602  # Administrator
    authenticate(username, client)

    response = client.get(_url(other_user_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_should_not_return_a_password(client: TestClient) -> None:
    username = find_username("Principal Investigator", proposal_code="2020-2-DDT-005")
    authenticate(username, client)
    user_id = get_authenticated_user_id(client)
    response = client.get(_url(user_id))
    assert response.status_code == status.HTTP_200_OK
    for key in response.json().keys():
        assert "password" not in key.lower()


@pytest.mark.parametrize("username", [find_username("SALT Astronomer")])
def test_get_user_should_return_correct_user_details(
    username: str, client: TestClient, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)[username]

    authenticate(username, client)
    user_id = get_authenticated_user_id(client)

    response = client.get(_url(user_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == data


def test_get_user_should_allow_admin_to_get_other_user(client: TestClient) -> None:
    username = find_username("Administrator")
    authenticate(username, client)

    other_user_id = 6

    response = client.get(_url(other_user_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] != username
