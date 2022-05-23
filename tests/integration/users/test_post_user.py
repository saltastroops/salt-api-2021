import uuid
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, misauthenticate, not_authenticated

USERS_URL = "/users/"

TOKEN_URL = "/token"


def _random_string() -> str:
    return str(uuid.uuid4())[:8]


def _new_user_details(username: Optional[str] = None) -> Dict[str, Any]:
    _username = username if username else _random_string()
    return dict(
        username=_username,
        password=_random_string(),
        email=f"{_username}@example.com",
        given_name=_random_string(),
        family_name=_random_string(),
        institution_id=5,
    )


def test_post_user_should_be_allowed_for_unauthenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)

    response = client.post(USERS_URL, json=_new_user_details())
    assert response.status_code == status.HTTP_201_CREATED


def test_post_user_should_be_allowed_for_misauthenticated_user(
    client: TestClient,
) -> None:
    misauthenticate(client)

    response = client.post(USERS_URL, json=_new_user_details())
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "username",
    [
        "rajeev",  # Board member
        "mbackes",  # TAC chair
        "Nella",  # SALT astronomer
    ],
)
def test_post_user_should_be_allowed_for_authenticated_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)

    response = client.post(USERS_URL, json=_new_user_details())
    assert response.status_code == status.HTTP_201_CREATED


def test_post_user_should_return_400_if_username_exists_already(
    client: TestClient,
) -> None:
    authenticate("hettlage", client)
    existing_username = "eric"

    response = client.post(
        USERS_URL, json=_new_user_details(username=existing_username)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.json()["message"].lower()


def test_post_user_should_create_a_new_user(client: TestClient) -> None:
    new_user_details = _new_user_details()

    expected_user = new_user_details.copy()
    # add affiliation institution of the user
    expected_user["affiliations"] = [
        {
            "department": " ",
            "institution_id": expected_user["institution_id"],
            "name": "South African Astronomical Observatory",
            "partner_code": "RSA",
            "partner_name": "South Africa",
        }
    ]
    del expected_user["password"]
    del expected_user["institution_id"]
    expected_user["alternative_emails"] = []
    expected_user["roles"] = []

    # check properties other than the password and id of the created user
    response = client.post(USERS_URL, json=new_user_details)
    created_user = response.json()
    del created_user["id"]
    assert response.status_code == status.HTTP_201_CREATED
    assert created_user == expected_user

    # It would be nice to check the password as well, but as the authentication method
    # is replaced with a dummy one for testing, we cannot easily be achieved. The
    # password should thus rather be tested implicitly as part of an end-to-end test for
    # creating a new user.
