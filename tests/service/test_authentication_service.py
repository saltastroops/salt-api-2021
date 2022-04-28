from datetime import datetime, timedelta
from typing import Optional, cast

import pytest
from freezegun import freeze_time
from pydantic import EmailStr

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.user import Institution, User
from saltapi.settings import Settings

TEST_DATA_PATH = "service/authentication_service.yaml"
SECRET_KEY = Settings().secret_key
FAKE_SECRET_KEY = "Fake Key"
ALGORITHM = "HS256"
USER = User(
    username="jdoe",
    family_name="Doe",
    given_name="John",
    id=1,
    email=EmailStr("jdoe@email.com"),
    alternative_emails=[EmailStr("")],
    password_hash="PasswordHash",
    affiliations=[
        Institution(
            institution_id=1,
            institution="Ins",
            department="Dept",
            partner_code="Partner",
        )
    ],
    roles=[],
)


class FakeUserRepository:
    def get(self, username: str) -> Optional[User]:
        if username == "jdoe":
            return User(
                id=1,
                username="jdoe",
                given_name="John",
                family_name="Doe",
                email=EmailStr("johndoe@email.com"),
                password_hash="hashedpassword",
                alternative_emails=[EmailStr("alt@gmail.com")],
                affiliations=[
                    Institution(
                        institution_id=1332,
                        institution="Other",
                        department="Other",
                        partner_code="Part",
                    )
                ],
                roles=[],
            )
        return None

    def find_user_with_username_and_password(
        self, username: str, password: str
    ) -> User:
        if username == "jdoe" and password == "hashedpassword":
            return User(
                id=1,
                username="jdoe",
                given_name="John",
                family_name="Doe",
                email=EmailStr("johndoe@email.com"),
                password_hash="hashedpassword",
                alternative_emails=[EmailStr("")],
                affiliations=[
                    Institution(
                        institution_id=1332,
                        institution="Other",
                        department="Other",
                        partner_code="Code",
                    )
                ],
                roles=[],
            )

        raise NotFoundError("User not found or password doesn't match.")


user_repository = cast(UserRepository, FakeUserRepository())


def test_access_token_by_default_expires_in_seven_days() -> None:
    with freeze_time("2021-10-17 12:00:01"):
        authentication_service = AuthenticationService(user_repository)
        access_token = authentication_service.access_token(USER)
        now = datetime.now()
        assert access_token.expires_at == now + timedelta(days=7)


@pytest.mark.parametrize("token_lifetime_hours", [10, 200, 0, -10])
def test_access_token_expires_in_given_hours(token_lifetime_hours: int) -> None:
    with freeze_time("2021-10-17 12:00:01"):
        now = datetime.now()
        access_token = AuthenticationService.access_token(USER, token_lifetime_hours)
        assert access_token.expires_at == now + timedelta(hours=token_lifetime_hours)


def test_access_token_has_type_bearer() -> None:
    access_token = AuthenticationService.access_token(USER)
    assert access_token.token_type == "bearer"


def test_authenticate_user_returns_correct_user() -> None:
    authentication_service = AuthenticationService(user_repository)
    user = authentication_service.authenticate_user("jdoe", "hashedpassword")

    assert user.id == 1
    assert user.username == "jdoe"
    assert user.given_name == "John"
    assert user.email == "johndoe@email.com"


@pytest.mark.parametrize(
    "username, password",
    [
        ("noUser", "hashedpassword"),
        ("", "hashedpassword"),
        ("jdoee", "hashedpassword"),
        (None, "hashedpassword"),
    ],
)
def test_authenticate_user_raises_error_for_wrong_user(
    username: str, password: str
) -> None:
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(username, password)


@pytest.mark.parametrize(
    "username, password",
    [
        ("jdoe", "hashedpasswordd"),
        ("jdoe", "wrongpassword"),
        ("jdoe", ""),
        ("jdoe", None),
        (None, None),
    ],
)
def test_authenticate_user_raises_error_for_wrong_password(
    username: str, password: str
) -> None:
    authentication_service = AuthenticationService(user_repository)
    with pytest.raises(NotFoundError):
        authentication_service.authenticate_user(username, password)
