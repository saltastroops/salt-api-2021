from datetime import datetime, timedelta
from typing import Any, Callable

import pytest
from freezegun import freeze_time
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.settings import Settings

from saltapi.service.authentication_service import AuthenticationService
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

# tested by mypy
# def test_access_token_returns_access_token(
#         dbconnection: Connection
# ) -> None:
#     user_repository = FakeUserRepository(dbconnection)
#     authentication_service = AuthenticationService(user_repository)
#     access_token = authentication_service.access_token(USER)
#     assert str(type(access_token)) == \
#            "<class 'saltapi.service.authentication.AccessToken'>"


def test_access_token_expire_in_seven_days_default(
        dbconnection: Connection
) -> None:
    freezer = freeze_time("2021-10-17 12:00:01")
    freezer.start()
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    today = datetime.today()
    # you can use something like freeze gut to set a time static
    assert access_token.expires_at.date() == (today + timedelta(days=7)).date()
    freezer.stop()


def test_access_token_expire_in_given_days(
        dbconnection: Connection
) -> None:
    freezer = freeze_time("2021-10-17 12:00:01")
    freezer.start()
    today = datetime.today()
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER, 10)
    assert access_token.expires_at == (today + timedelta(days=10))
    access_token = authentication_service.access_token(USER, 15)
    assert access_token.expires_at == (today + timedelta(days=15))
    access_token = authentication_service.access_token(USER, 3)
    assert access_token.expires_at == (today + timedelta(days=3))
    access_token = authentication_service.access_token(USER, 0)
    assert access_token.expires_at == (today)
    freezer.stop()


def test_access_token_has_type_bearer(
        dbconnection: Connection
) -> None:
    user_repository = FakeUserRepository(dbconnection)
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


def test_authenticate_user_raise_error_for_wrong_password(
    dbconnection: Connection
) -> None:
    user_repository = FakeUserRepository(dbconnection)
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(
        "jdoe", "wrongpassword")

    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(
        "jdoe", '')

    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(
        "jdoe", None)


