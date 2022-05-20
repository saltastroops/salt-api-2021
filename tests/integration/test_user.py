from typing import Callable

import pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.service.user import User
from tests.conftest import authenticate, misauthenticate

USER_URL = "/user"


def test_should_return_401_if_user_is_not_authenticated(client: TestClient) -> None:
    response = client.get(USER_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_401_if_user_uses_invalid_token(client: TestClient) -> None:
    misauthenticate(client)
    response = client.get(USER_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "username", ["ejk", "lcrause", "nerasmus", "mbackes", "nhlavutelo", "mbackes"]
)
def test_should_return_the_correct_user_details(
    username: str, client: TestClient, check_user: Callable[[User], None]
) -> None:
    authenticate(username, client)
    response = client.get(USER_URL)
    user_details = response.json()
    check_user(user_details)
