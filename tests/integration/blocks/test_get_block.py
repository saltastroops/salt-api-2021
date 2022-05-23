import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, not_authenticated

BLOCKS_URL = "/blocks"


def test_should_return_401_when_requesting_a_block_for_unauthenticated_user(
    client: TestClient,
) -> None:
    block_id = 1

    not_authenticated(client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id),
        params={"block_id": block_id},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_non_existing_block(
    client: TestClient,
) -> None:
    block_id = -1

    username = "cmofokeng"  # Administrator
    authenticate(username, client)
    response = client.get(
        BLOCKS_URL + "/" + str(block_id),
        params={"block_id": block_id},
    )
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
def test_should_return_a_block_when_requesting_block_for_permitted_user(
    username: str, client: TestClient
) -> None:
    block_id = 80779  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(BLOCKS_URL + "/" + str(block_id))
    assert response.status_code == status.HTTP_200_OK
    assert "proposal_code" in response.json()
    assert "semester" in response.json()
    assert "block_visits" in response.json()


@pytest.mark.parametrize(
    "username",
    [
        "Srianand",  # Investigator
        "gitika",  # Principal Contact
        "ngupta",  # Principal Investigator
        "marek",  # TAC Member
        "tkastr",  # TAC Chair
    ],
)
def test_should_return_403_when_requesting_block_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    block_id = 80779  # belongs to proposal 2019-2-SCI-006

    authenticate(username, client)
    response = client.get(BLOCKS_URL + "/" + str(block_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN
