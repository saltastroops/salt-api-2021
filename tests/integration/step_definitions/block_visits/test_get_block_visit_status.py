from fastapi.testclient import TestClient
from pytest_bdd import parsers, scenarios, then, when
from requests import Response
from starlette.status import HTTP_200_OK

scenarios("../../features/block_visits/get_block_visit_status.feature")

BLOCK_VISIT_URL = "/block-visits"


@when(
    parsers.parse("I request a block visit {block_visit_id} status"),
    target_fixture="response",
)
def request_block_visit(block_visit_id: int, client: TestClient) -> Response:
    response = client.get(BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status")
    return response


@then(parsers.parse("I get a block visit {block_visit_id} status {status_value}"))
def block_visit(block_visit_id: int, status_value: str, client: TestClient) -> None:
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id) + "/status",
        params={"proposal_code": "2016-1-COM-001"},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == status_value
