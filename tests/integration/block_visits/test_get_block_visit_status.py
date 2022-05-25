import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, find_username, not_authenticated

BLOCK_VISIT_URL = "/block-visits"


def test_should_return_401_when_requesting_block_visit_status_for_unauthenticated_user(
    client: TestClient,
) -> None:
    block_visit_id = 1
    not_authenticated(client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status",
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_status_of_non_existing_block_visit(
    client: TestClient,
) -> None:
    block_visit_id = -1
    user = find_username("Administrator")
    authenticate(user, client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status",
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2019-2-SCI-006"),
        find_username("Principal Contact", proposal_code="2019-2-SCI-006"),
        find_username("Principal Investigator", proposal_code="2019-2-SCI-006"),
        find_username("Administrator"),
        find_username("SALT Astronomer"),
        find_username("TAC Member", partner_code="RSA"),
    ],
)
def test_should_return_block_visit_status_for_permitted_users(
    username: str, client: TestClient
) -> None:
    block_visit_id = 25392  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status",
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() != ""


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2019-2-SCI-006"),
        find_username("Principal Contact", proposal_code="2019-2-SCI-006"),
        find_username("Principal Investigator", proposal_code="2019-2-SCI-006"),
        find_username("Board Member"),
    ],
)
def test_should_return_403_for_get_block_visit_status_for_non_permitted_users(
    username: str, client: TestClient
) -> None:
    block_visit_id = 1

    authenticate(username, client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status",
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
