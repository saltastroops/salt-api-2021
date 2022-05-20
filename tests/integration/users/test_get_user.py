from typing import Any, Callable

import pytest as pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.web.schema.user import User
from tests.conftest import (
    authenticate,
    find_username,
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

    response = client.get(_url(1602))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_should_return_401_for_user_with_invalid_auth_token(
    client: TestClient,
) -> None:
    misauthenticate(client)

    response = client.get(_url(1602))
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
    other_user_id = 1602
    authenticate(username, client)

    response = client.get(_url(other_user_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_should_not_return_a_password(client: TestClient) -> None:
    username = find_username("Principal Investigator", proposal_code="2020-2-DDT-005")
    authenticate(username, client)

    response = client.get(_url(763))
    assert response.status_code == status.HTTP_200_OK
    for key in response.json().keys():
        assert "password" not in key.lower()


@pytest.mark.parametrize("username, user_id", [("cmofokeng", 1602), ("lcrause", 6)])
def test_get_user_should_return_correct_user_details(
    username: str,
    user_id: int,
    client: TestClient,
    testdata: Callable[[str], Any],
    check_user: Callable[[User], None],
) -> None:
    authenticate(username, client)

    response = client.get(_url(user_id))
    user_details = response.json()
    check_user(user_details)


def test_get_user_should_allow_admin_to_get_other_user(
    client: TestClient, check_user: Callable[[User], None]
) -> None:
    username = "cmofokeng"
    authenticate(username, client)

    other_username = find_username(
        "Principal Investigator", proposal_code="2020-2-DDT-005"
    )

    response = client.get(_url(6))
    user_details = response.json()
    check_user(user_details)
