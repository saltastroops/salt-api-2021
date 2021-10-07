import pytest
from fastapi.testclient import TestClient
from requests import Response
from starlette import status

from saltapi.settings import Settings
from tests.conftest import read_testdata, TEST_DATA, authenticate

PROPOSALS_URL = "/proposals"

USERS = read_testdata(TEST_DATA)
SECRET_KEY = Settings().secret_key


def get_proposal(proposal_code: str, username: str, client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL + "/" + proposal_code,
                          params={
                              "proposal_code": proposal_code,
                              "user": authenticate(username, client)
                          })
    return response


# Getting a proposal for permitted users
@pytest.mark.parametrize(
    "user_type",
    [
        'investigators',
    ],
)
def test_get_proposal(user_type: str, client: TestClient) -> None:
    proposals_info = USERS[user_type]
    for proposal_code, username in proposals_info.items():
        response = get_proposal(proposal_code, username, client)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["proposal_code"] == proposal_code
