from fastapi.testclient import TestClient
from pytest_bdd import parsers, scenarios, then, when
from requests import Response
from starlette.status import HTTP_200_OK

TOKEN_URL = "/token"


scenarios("../../features/authentication/authentication.feature")


@when("I try to login with an incorrect username", target_fixture="response")
def login_with_incorrect_username(client: TestClient) -> Response:
    response = client.post(
        TOKEN_URL, data={"username": "idontexist", "password": "secret"}
    )
    return response


@when("I try to login with an invalid password", target_fixture="response")
def login_with_invalid_password(client: TestClient) -> Response:
    response = client.post(
        TOKEN_URL, data={"username": "hettlage", "password": "wrongpassword"}
    )
    return response


@when("I login with valid credentials", target_fixture="response")
def logion_with_valid_credentials(client: TestClient) -> Response:
    response = client.post(
        TOKEN_URL, data={"username": "hettlage", "password": "secret"}
    )
    return response


@then("I get an authorization token")
def authentication_token(response: Response) -> None:
    assert response.status_code == HTTP_200_OK
    assert "access_token" in response.json()


@then(parsers.parse("I get a message containing {text}"))
def message_containing(text: str, response: Response) -> None:
    assert text in response.json()["detail"]
