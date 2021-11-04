import uuid
from typing import Dict, Optional

import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import (
    authenticate,
    create_user,
    find_username,
    misauthenticate,
    not_authenticated,
)

USERS_URL = "/users/"


def _url(username: str) -> str:
    return USERS_URL + username


def _patch_data(
    username: Optional[str] = None, password: Optional[str] = None
) -> Dict[str, Optional[str]]:
    return {"username": username, "password": password}


def test_patch_user_should_return_401_for_unauthenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)

    response = client.patch(_url("nhlavutelo"), json=_patch_data())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_user_should_return_401_for_user_with_invalid_auth_token(
    client: TestClient,
) -> None:
    misauthenticate(client)

    response = client.patch(_url("nhlavutelo"), json=_patch_data())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_user_should_return_404_for_non_existing_user(client: TestClient) -> None:
    username = find_username("Administrator")
    authenticate(username, client)

    response = client.patch(_url("idontexist"), json=_patch_data())
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        find_username("Board Member"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("SALT Astronomer"),
    ],
)
def test_patch_user_should_return_403_if_non_admin_tries_to_update_other_user(
    username: str, client: TestClient
) -> None:
    other_username = find_username(
        "Principal Investigator", proposal_code="2020-2-DDT-005"
    )
    authenticate(username, client)

    response = client.patch(_url(other_username), json=_patch_data())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_patch_user_should_keep_existing_values_by_default(client: TestClient) -> None:
    username = create_user(client)
    authenticate(username, client)

    current_user_details = client.get(_url(username)).json()
    client.patch(_url(username), json={})
    updated_user_details = client.get(_url(username)).json()

    assert updated_user_details == current_user_details


def test_patch_user_should_update_with_new_values(client: TestClient) -> None:
    username = create_user(client)
    new_username = str(uuid.uuid4())[:8]
    authenticate(username, client)

    current_user_details = client.get(_url(username)).json()
    user_update = {"username": new_username, "password": "very_very_secret"}
    expected_updated_user_details = current_user_details.copy()
    expected_updated_user_details.update(user_update)
    del expected_updated_user_details["password"]

    # the endpoint returns the correct response...
    response = client.patch(_url(username), json=user_update)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_updated_user_details

    # ... and the user is indeed updated
    updated_user_details = client.get(_url(new_username)).json()
    assert updated_user_details == expected_updated_user_details


def test_patch_user_should_be_idempotent(client: TestClient) -> None:
    username = create_user(client)
    new_username = str(uuid.uuid4())[:8]
    authenticate(username, client)

    current_user_details = client.get(_url(username)).json()
    user_update = {"username": new_username, "password": "very_very_secret"}
    expected_updated_user_details = current_user_details.copy()
    expected_updated_user_details.update(user_update)
    del expected_updated_user_details["password"]

    client.patch(_url(username), json=user_update)
    client.patch(_url(new_username), json=user_update)
    client.patch(_url(new_username), json=user_update)

    updated_user_details = client.get(_url(new_username)).json()
    assert updated_user_details == expected_updated_user_details


def test_patch_user_should_allow_admin_to_update_other_user(client: TestClient) -> None:
    username = create_user(client)
    new_username = str(uuid.uuid4())[:8]
    authenticate(find_username("Administrator"), client)

    current_user_details = client.get(_url(username)).json()
    user_update = {"username": new_username, "password": "very_very_secret"}
    expected_updated_user_details = current_user_details.copy()
    expected_updated_user_details.update(user_update)
    del expected_updated_user_details["password"]

    response = client.patch(_url(username), json=user_update)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_updated_user_details
