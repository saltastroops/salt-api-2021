from fastapi.testclient import TestClient
from pytest_bdd import parsers, scenarios, then, when
from requests import Response
from starlette import status

scenarios("../../features/block_visits/get_block_visit.feature")

BLOCK_VISIT_URL = "/block-visits"


@when(
    parsers.parse("I request a block visit {block_visit_id}"), target_fixture="response"
)
def request_block_visit(block_visit_id: int, client: TestClient) -> Response:
    response = client.get(
        BLOCK_VISIT_URL + "/" + str(block_visit_id),
    )
    return response


@then(parsers.parse("I get the block visit {block_visit_id}"))
def block_visit(response: Response) -> None:
    assert response.status_code == status.HTTP_200_OK
