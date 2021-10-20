from fastapi.testclient import TestClient
from starlette import status

TOKEN_URL = "/token"


def test_should_return_401_if_you_login_with_incorrect_username(
    client: TestClient,
) -> None:
    response = client.post(
        TOKEN_URL, data={"username": "idontexist", "password": "secret"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_401_if_you_login_with_invalid_password(client: TestClient) -> None:
    response = client.post(
        TOKEN_URL, data={"username": "hettlage", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_a_token_if_you_login_with_valid_credentials(
    client: TestClient,
) -> None:
    response = client.post(
        TOKEN_URL, data={"username": "hettlage", "password": "secret"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
