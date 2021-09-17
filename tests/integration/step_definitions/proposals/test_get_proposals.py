from pytest_bdd import when, scenarios, then
from fastapi.testclient import TestClient
from requests import Response


scenarios("../../features/proposals/get_proposals.feature")


PROPOSALS_URL = "/proposals"


@when("I request a list of proposals", target_fixture="response")
def i_request_proposals(client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL)

    return response


@when("I request a list of proposals from <from_semester> to <to_semester>", target_fixture="response")
def I_request_proposals_for_range(from_semester: str, to_semester: str, client: TestClient) -> Response:
    if from_semester == 'any':
        from_semester = None
    if to_semester == 'any':
        to_semester = None
    params = {}
    if from_semester:
        params["from_semester"] = from_semester
    if to_semester:
        params["to_semester"] = to_semester
    response = client.get(PROPOSALS_URL, params=params)

    return response
