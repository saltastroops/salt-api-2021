from fastapi.testclient import TestClient
from pytest_bdd import scenarios, then, when
from requests import Response

scenarios("../../features/proposals/get_proposals.feature")


PROPOSALS_URL = "/proposals"


@when("I request a list of proposals", target_fixture="response")
def i_request_proposals(client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL)

    return response


@when(
    "I request a list of proposals from <from_semester> to <to_semester>",
    target_fixture="response",
)
def I_request_proposals_for_range(
    from_semester: str, to_semester: str, client: TestClient
) -> Response:
    _from_semester = from_semester if from_semester.lower() != "none" else None
    _to_semester = to_semester if to_semester.lower() != "none" else None
    params = {}
    if _from_semester:
        params["from"] = _from_semester
    if _to_semester:
        params["to"] = _to_semester
    response = client.get(PROPOSALS_URL, params=params)

    return response


@when(
    "I request a list of proposals with a negative maximum number of results",
    target_fixture="response",
)
def i_request_a_list_of_proposals_with_negative_limit(client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL, params={"limit": -1})

    return response


@then("I get the <proposal_count> proposals <proposal_codes>")
def i_get_the_proposals(
    proposal_count: int, proposal_codes: str, response: Response
) -> None:
    expected_proposal_count = int(proposal_count)
    expected_proposal_code_list = sorted(
        [pc.strip() for pc in proposal_codes.split(",") if pc.strip()]
    )

    proposal_code_list = sorted(p["proposal_code"] for p in response.json())
    assert len(proposal_code_list) == expected_proposal_count
    if expected_proposal_code_list != ["many"]:
        assert proposal_code_list == expected_proposal_code_list


@when("I request a list of up to <limit> proposals", target_fixture="response")
def i_request_up_to_limit_proposals(limit: str, client: TestClient) -> Response:
    response = client.get(PROPOSALS_URL, params={"limit": int(limit)})

    return response


@then("I get <limit> proposals")
def i_get_limit_proposal(limit: str, response: Response) -> None:
    assert len(response.json()) == int(limit)


@then("I get 1000 proposals")
def i_get_1000_proposals(response: Response) -> None:
    assert len(response.json()) == 1000
