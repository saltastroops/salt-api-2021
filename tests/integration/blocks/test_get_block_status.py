import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, find_username, not_authenticated

BLOCKS_URL = "/blocks"


def test_should_return_401_when_requesting_block_status_for_unauthenticated_user(
    client: TestClient,
) -> None:
    block_id = 1

    not_authenticated(client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id) + "/status",
        params={"block_id": block_id},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_block_status_non_existing_block(
    client: TestClient,
) -> None:
    block_id = -1

    user = find_username("Administrator")
    authenticate(user, client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id) + "/status",
        params={"block_id": block_id},
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
def test_should_return_block_status_when_requesting_block_status_for_permitted_users(
    username: str, client: TestClient
) -> None:
    block_id = 80779  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id) + "/status",
        params={"block_id": block_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "value" in [s for s in response.json()]
    assert "reason" in [s for s in response.json()]


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2020-2-DDT-005"),
        find_username("Principal Contact", proposal_code="2020-2-DDT-005"),
        find_username("Principal Investigator", proposal_code="2020-2-DDT-005"),
        find_username("TAC Member", partner_code="POL"),
        find_username("TAC Chair", partner_code="POL"),
    ],
)
def test_should_return_403_when_requesting_block_status_for_non_permitted_users(
    username: str, client: TestClient
) -> None:
    block_id = 80779

    authenticate(username, client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id) + "/status",
        params={"block_id": block_id},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
