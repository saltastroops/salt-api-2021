from typing import Any, Callable

from fastapi.testclient import TestClient
from starlette import status

WHO_AM_I_URL = "/who-am-i"

USER_DATA = "api/who_am_i.yaml"


def test_should_return_401_if_user_is_not_authenticated(client: TestClient) -> None:
    response = client.get(WHO_AM_I_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_401_if_user_uses_invalid_token(
    client: TestClient, misauthenticate: Callable[[TestClient], None]
) -> None:
    misauthenticate(client)
    response = client.get(WHO_AM_I_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_the_correct_user_details(
    client: TestClient,
    authenticate: Callable[[str, TestClient], None],
    testdata: Callable[[str], Any],
) -> None:
    data = testdata(USER_DATA)["who_am_i"]

    for d in data:
        username = d["username"]
        expected_user_details = d
        expected_user_details["roles"] = set(expected_user_details["roles"])

        authenticate(username, client)

        response = client.get(WHO_AM_I_URL)
        user_details = response.json()
        user_details["roles"] = set(user_details["roles"])

        assert response.status_code == status.HTTP_200_OK
        assert user_details == expected_user_details
