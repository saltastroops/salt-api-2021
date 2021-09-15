from fastapi.testclient import TestClient
from pytest_bdd import parsers, scenarios, then, when
from requests import Response
from starlette.status import HTTP_200_OK

scenarios("../../features/proposals/get_proposal.feature")

PROPOSALS_URL = "/proposals"


@when(
    parsers.parse("I request the proposal {proposal_code}"), target_fixture="response"
)
def request_proposal(proposal_code: str, client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL + "/" + proposal_code)
    return response


@then(parsers.parse("I get the proposal {proposal_code}"))
def proposal(proposal_code: str, response: Response) -> None:
    assert response.status_code == HTTP_200_OK
    assert response.json()["proposal_code"] == proposal_code
