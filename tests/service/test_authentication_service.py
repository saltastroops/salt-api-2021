from datetime import datetime, timedelta
from typing import Any, Callable

import pytest
from jose import JWTError, jwt
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.settings import Settings

from saltapi.service.authentication_service import AuthenticationService, \
    get_current_user
from saltapi.service.user import User
from tests.repository.fake_user_repository import FakeUserRepository

TEST_DATA_PATH = "service/authentication_service.yaml"
SECRET_KEY = Settings().secret_key
FAKE_SECRET_KEY = 'Fake Key'
ALGORITHM = Settings().algorithm
USER = User(
    username="jdoe",
    family_name="Doe",
    given_name="John",
    id=1,
    email="jdoe@email.com",
    password_hash="PasswordHash"
)


def test_access_token_returns_access_token(
        dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    user_repository = UserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    assert str(type(access_token)) == \
           "<class 'saltapi.service.authentication.AccessToken'>"


def test_access_token_expire_in_seven_days(
        dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    user_repository = UserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    today = datetime.today()
    assert access_token.expires_at.date() == (today + timedelta(days=7)).date()


def test_access_token_has_type_bearer(
        dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    user_repository = UserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    assert access_token.token_type == 'bearer'


def test_authenticate_user_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected = testdata(TEST_DATA_PATH)["authenticate_user"]
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    user = authentication_service.authenticate_user(
        expected["username"], expected["password_hash"])

    assert user.id == expected["id"]
    assert user.username == expected["username"]
    assert user.given_name == expected["given_name"]
    assert user.email is not None


def test_authenticate_user_raise_error_for_no_user(
    dbconnection: Connection
) -> None:
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(
        "noUser", "noPassword")


def test_jwt_token_encode_correct_payload(dbconnection: Connection) -> None:
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    payload = {"id": 9, "name": "John"}
    token = authentication_service.jwt_token(payload)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["id"] == 9
    assert decoded["name"] == "John"


def test_jwt_token_can_not_be_decoded_with_wrong_key(dbconnection: Connection) -> None:
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    payload = {"id": 9, "name": "John"}
    token = authentication_service.jwt_token(payload)
    with pytest.raises(JWTError):
        jwt.decode(token, FAKE_SECRET_KEY, algorithms=[ALGORITHM])


def test_validate_auth_token_can_verify_token(dbconnection: Connection) -> None:
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    token = access_token.access_token

    # Test valid token. For valid token User is returned
    user = authentication_service.validate_auth_token(token)
    assert user.username == "jdoe"
    assert user.given_name == "John"

    #  Test if token is tempered error is raise
    with pytest.raises(JWTError):
        authentication_service.validate_auth_token(token+'i')

    # Test error raised for invalid token
    with pytest.raises(JWTError):
        authentication_service.validate_auth_token('invalidToken')
