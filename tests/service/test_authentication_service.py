from datetime import datetime, timedelta
from typing import Any, Callable, Optional, cast

import pytest
from freezegun import freeze_time

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.settings import Settings

from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.user import User

TEST_DATA_PATH = "service/authentication_service.yaml"
SECRET_KEY = Settings().secret_key
FAKE_SECRET_KEY = 'Fake Key'
ALGORITHM = "HS256"
USER = User(
    username="jdoe",
    family_name="Doe",
    given_name="John",
    id=1,
    email="jdoe@email.com",
    password_hash="PasswordHash"
)


class FakeUserRepository():
    def get(self, username: str) -> Optional[User]:
        if username == "jdoe":
            return User(
                id=1,
                username='jdoe',
                given_name="John",
                family_name="Doe",
                email="johndoe@email.com",
                password_hash="hasdedpassword"
            )
        return None

    def find_user_with_username_and_password(self,username, password):
        if username == "jdoe" and password == "hasdedpassword":
            return User(
                id=1,
                username='jdoe',
                given_name="John",
                family_name="Doe",
                email="johndoe@email.com",
                password_hash="hasdedpassword"
            )

        raise NotFoundError("User not found or password doesn't match.")


user_repository = cast(UserRepository, FakeUserRepository())


def test_access_token_by_default_expires_in_seven_days(
) -> None:
    with freeze_time("2021-10-17 12:00:01"):
        authentication_service = AuthenticationService(user_repository)
        access_token = authentication_service.access_token(USER)
        today = datetime.today()
        # you can use something like freeze gut to set a time static
        assert access_token.expires_at == (today + timedelta(days=7))

@pytest.mark.parametrize(
"user, token_lifetime_hours",
    [
        (USER, 10),
        (USER, 200),
        (USER, 0),
        (USER, -10),
    ]
)
def test_access_token_expire_in_given_hours(user: User, token_lifetime_hours: int) -> None:
    with freeze_time("2021-10-17 12:00:01"):
        today = datetime.today()
        authentication_service = AuthenticationService(user_repository)
        access_token = authentication_service.access_token(USER,  token_lifetime_hours)
        assert access_token.expires_at == (today + timedelta(hours=token_lifetime_hours))



def test_access_token_has_type_bearer(
) -> None:
    authentication_service = AuthenticationService(user_repository)
    access_token = authentication_service.access_token(USER)
    assert access_token.token_type == 'bearer'


def test_authenticate_user_returns_correct_user() -> None:
    authentication_service = AuthenticationService(user_repository)
    user = authentication_service.authenticate_user(
        "jdoe", "hasdedpassword")

    assert user.id == 1
    assert user.username == "jdoe"
    assert user.given_name == "John"
    assert user.email == "johndoe@email.com"


@pytest.mark.parametrize(
    "username, password",
    [
        ("noUser", "hasdedpassword"),
        ("", "hasdedpassword"),
        ("jdoee", "hasdedpassword"),
    ]
)
def test_authenticate_user_raises_error_for_wrong_user(
        username: str, password: str) -> None:
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(username, password)


@pytest.mark.parametrize(
    "username, password",
    [
        ("jdoe", "hasdedpasswordd"),
        ("jdoe", "wrongpassword"),
        ("jdoe", ""),
    ]
)
def test_authenticate_user_raise_error_for_wrong_password(
        username: str, password: str) -> None:
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(username, password)
