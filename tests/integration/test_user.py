from typing import Any, Callable

from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, misauthenticate

USER_URL = "/user"

USER_DATA = "integration/user.yaml"


def test_should_return_401_if_user_is_not_authenticated(client: TestClient) -> None:
    response = client.get(USER_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_401_if_user_uses_invalid_token(client: TestClient) -> None:
    misauthenticate(client)
    response = client.get(USER_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_the_correct_user_details(
    client: TestClient,
    testdata: Callable[[str], Any],
) -> None:
    data = testdata(USER_DATA)["who_am_i"]

    for d in data:
        username = d["username"]
        expected_user_details = d
        expected_user_details["roles"] = set(expected_user_details["roles"])

        authenticate(username, client)

        response = client.get(USER_URL)
        user_details = response.json()
        user_details["roles"] = set(user_details["roles"])

        assert response.status_code == status.HTTP_200_OK
        assert user_details == expected_user_details
