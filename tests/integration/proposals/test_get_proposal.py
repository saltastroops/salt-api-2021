import pytest
from fastapi.testclient import TestClient
from starlette import status

from saltapi.settings import Settings
from tests.conftest import read_testdata, TEST_DATA, authenticate, not_authenticated

PROPOSALS_URL = "/proposals"

USERS = read_testdata(TEST_DATA)
SECRET_KEY = Settings().secret_key


# Unauthenticated user cannot request a proposal
def test_get_proposal_for_nonpermitted_user(client: TestClient) -> None:
    proposal_code = list(USERS["investigators"].keys())[0]
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code, "user": not_authenticated(client)},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Non-existing proposals cannot be found
def test_get_nonexisting_proposal(client: TestClient) -> None:
    username = list(USERS["investigators"].values())[0]
    proposal_code = "2020-2-SCI-099"
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code, "user": authenticate(username, client)},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Getting a proposal for permitted users
@pytest.mark.parametrize(
    "user_type",
    [
        "investigators",
        "principal_investigators" "administrator",
        "salt_astronomer",
        "tac_members",
    ],
)
def test_get_proposal_for_permitted_users(user_type: str, client: TestClient) -> None:
    data: dict = {"proposal_code": [], "username": []}

    if user_type == "administrator" or user_type == "salt_astronomer":
        # an administrator and a salt-astronomer can check any proposal
        username = USERS[user_type]
        proposals_info = USERS["investigators"]

        for proposal_code in proposals_info.keys():
            data["proposal_code"].append(proposal_code)
            data["username"].append(username)

    elif user_type == "tac_members":
        # a tac-member can only check a proposal they affiliated partner to
        username = USERS[user_type]["RSA"]
        for i, proposal_code in enumerate(USERS["investigators"].keys()):
            if i in [0, 1, 5]:
                data["proposal_code"].append(proposal_code)
                data["username"].append(username)

    else:
        # an investigator can only check a proposal that belongs to them
        for proposal_code, username in USERS[user_type].items():
            data["proposal_code"].append(proposal_code)
            data["username"].append(username)

    for i in range(len(data["proposal_code"])):
        proposal_code = data["proposal_code"][i]
        username = data["username"][i]
        response = client.get(
            PROPOSALS_URL + "/" + proposal_code,
            params={
                "proposal_code": proposal_code,
                "user": authenticate(username, client),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["proposal_code"] == proposal_code


# Getting a proposal is not permitted for some users
@pytest.mark.parametrize(
    "user_type",
    [
        "investigators",
        "principal_investigators",
        "principal_contacts",
    ],
)
def test_get_proposal_for_nonpermitted_users(
    user_type: str, client: TestClient
) -> None:
    proposal_code = list(USERS[user_type].keys())[0]
    username = list(USERS[user_type].values())[1]
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code, "user": authenticate(username, client)},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
