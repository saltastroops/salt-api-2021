import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, find_username, not_authenticated

BLOCK_VISIT_URL = "/block-visits"


def test_should_return_401_when_requesting_block_visit_for_unauthenticated_user(
    client: TestClient,
) -> None:
    block_visit_id = 1
    not_authenticated(client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id),
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_block_visit_for_non_existing_block_visit_id(
    client: TestClient,
) -> None:
    block_visit_id = -1
    user = find_username("Administrator")
    authenticate(user, client)
    response = client.get(BLOCK_VISIT_URL + "/" + str(block_visit_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        "rajeev",  # Investigator
        "karandis",  # Principal Contact
        "brent",  # Principal Investigator
        "cmofokeng",  # Administrator
        "Nella",  # SALT Astronomer
        "nerasmus",  # TAC Member
    ],
)
def test_should_return_block_visit_when_requesting_block_visit_for_permitted_users(
    username: str, client: TestClient
) -> None:
    block_visit_id = 25392  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id),
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert "status" in response.json()
    assert "rejection_reason" in response.json()


@pytest.mark.parametrize(
    "username",
    [
        "Srianand",  # Investigator
        "gitika",  # Principal Contact
        "ngupta",  # Principal Investigator
        "jph",  # TAC Member,
        "jph",  # TAC Chair,
        "mshara",  # Board Member
    ],
)
def test_should_return_403_when_requesting_block_visit_for_non_permitted_users(
    username: str, client: TestClient
) -> None:
    block_visit_id = 25392  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id),
        params={"block_visit_id": block_visit_id},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
