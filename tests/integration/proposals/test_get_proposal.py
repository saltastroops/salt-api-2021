import pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.settings import Settings
from tests.conftest import authenticate, not_authenticated, read_testdata

PROPOSALS_URL = "/proposals"

TEST_DATA = "users.yaml"

USERS = read_testdata(TEST_DATA)
SECRET_KEY = Settings().secret_key


def test_should_return_401_for_get_proposal_for_unauthorized_user(
    client: TestClient,
) -> None:
    proposal_code = "2019-2-SCI-006"
    not_authenticated(client)
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_401_for_get_non_existing_proposal(client: TestClient) -> None:
    username = USERS["administrator"]
    proposal_code = "2020-2-SCI-099"
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "user_type",
    [
        "investigators",
        "principal_investigators",
        "administrator",
        "salt_astronomer",
        "tac_members",
        "tac_chairs",
    ],
)
def test_should_return_proposal_for_get_proposal_for_permitted_users(
    user_type: str, client: TestClient
) -> None:
    proposal_code = "2018-2-LSP-001"
    username = ""

    if user_type == "investigators" or user_type == "principal_investigators":
        username = USERS[user_type][proposal_code]
    elif user_type == "administrator" or user_type == "salt_astronomer":
        username = USERS[user_type]
    else:
        username = USERS[user_type]["RSA"]

    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == proposal_code


@pytest.mark.parametrize(
    "user_type",
    ["investigators", "principal_investigators", "tac_members", "tac_chairs"],
)
def test_should_return_403_get_proposal_for_non_permitted_users(
    user_type: str, client: TestClient
) -> None:
    request_proposal_code = "2019-2-SCI-006"
    user_proposal_code = "2018-2-LSP-001"
    username = ""

    if user_type == "investigators" or user_type == "principal_investigators":
        username = USERS[user_type][user_proposal_code]
    elif user_type == "administrator" or user_type == "salt_astronomer":
        username = USERS[user_type]
    else:
        username = USERS[user_type]["UW"]

    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/" + request_proposal_code,
        params={"proposal_code": request_proposal_code},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
