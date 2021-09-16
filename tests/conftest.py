import os

import dotenv

# Make sure that the test database etc. are used.
# IMPORTANT: These lines must be executed before any server-related package is imported.
from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import User
from saltapi.service.user_service import UserService

os.environ["DOTENV_FILE"] = ".env.test"
dotenv.load_dotenv(os.environ["DOTENV_FILE"])


import re
from pathlib import Path
from typing import Any, Callable, Generator, Optional, cast

import pytest
import yaml
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then
from requests import Response
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from starlette import status

from saltapi.main import app
from saltapi.web.api.authentication import get_user_authentication_function as user_auth

engine: Optional[Engine] = None
sdb_dsn = os.environ.get("SDB_DSN")
if sdb_dsn:
    echo_sql = True if os.environ.get("ECHO_SQL") else False  # SQLAlchemy needs a bool
    engine = create_engine(sdb_dsn, echo=echo_sql, future=True)


# Replace the user authentication with one which assumes that every user has the
# password "secret".

USER_PASSWORD = "secret"


def get_user_authentication_function() -> Callable[[str, str], User]:
    def authenticate_user(username: str, password: str) -> User:
        if password != USER_PASSWORD:
            raise NotFoundError("No user found for username and password")

        with cast(Engine, engine).connect() as connection:
            user_repository = UserRepository(connection)
            user_service = UserService(user_repository)
            user = user_service.get_user(username)
            return user

    return authenticate_user


app.dependency_overrides[user_auth] = get_user_authentication_function


TEST_DATA = "users.yaml"


@pytest.fixture(scope="function")
def dbconnection() -> Generator[Connection, None, None]:
    if not engine:
        raise ValueError(
            "No SQLAlchemy engine set. Have you defined the SDB_DSN environment "
            "variable?"
        )
    with engine.connect() as connection:
        yield connection


def read_testdata(path: str) -> Any:
    if Path(path).is_absolute():
        raise ValueError("The file path must be a relative path.")

    root_dir = Path(__file__).parent.parent
    datafile = root_dir / "testdata" / path
    if not datafile.exists():
        raise FileNotFoundError(f"File does not exist: {datafile}")

    with open(datafile, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def testdata() -> Generator[Callable[[str], Any], None, None]:
    """
    Load test data from a YAML file.

    The test data must be contained in a YAML file located in the folder tests/testdata
    or any subfolder thereof. The file path relative to the tests/testdata folder must
    be passed as the argument of the function returned by this fixture.

    The YAML file must contain a single document only (i.e. it must contain no "---"
    separators). Its content is returned in the way PyYAML returns YAML content.
    """

    yield read_testdata


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)


@given("I am <user_type>")
def i_am(user_type: str, client: TestClient) -> None:
    if user_type == "not authenticated":
        not_authenticated(client)
        return

    groups = re.match(
        r"(?:an )?investigator (?:for|of) (?:the )?proposal ([-\w\d]+)", user_type
    )
    if groups:
        authenticate(investigator(groups.group(1)), client)
        return

    groups = re.match(
        r"(?:a )?[Pp]rincipal [Ii]nvestigator (?:for|of) (?:the )?proposal ([-\w\d]+)",
        user_type,
    )
    if groups:
        authenticate(principal_investigator(groups.group(1)), client)
        return

    groups = re.match(
        r"(?:an )?[Pp]rincipal [Cc]ontact (?:for|of) (?:the )?proposal ([-\w\d]+)",
        user_type,
    )
    if groups:
        authenticate(principal_contact(groups.group(1)), client)
        return

    groups = re.match(
        r"(?:a )?TAC [Cc]hair (?:for|of) (?:the )?partner (\w+)", user_type
    )
    if groups:
        authenticate(tac_chair(groups.group(1)), client)
        return

    groups = re.match(
        r"(?:a )?TAC [Mm]ember (?:for|of) (?:the )?partner (\w+)", user_type
    )
    if groups:
        authenticate(tac_member(groups.group(1)), client)
        return

    groups = re.match(r"(?:a )?Board member", user_type)
    if groups:
        authenticate(board_member(), client)
        return

    groups = re.match(r"(?:a )?partner affilated user", user_type)
    if groups:
        authenticate(partner_affiliated_user(), client)
        return

    groups = re.match(r"(?:a )?non[- ]partner affilated user", user_type)
    if groups:
        authenticate(non_partner_affiliated_user(), client)
        return

    groups = re.match(r"(?:a )?SALT [Aa]stronomer", user_type)
    if groups:
        authenticate(salt_astronomer(), client)
        return

    groups = re.match(r"(?:an )?[Aa]dministrator", user_type)
    if groups:
        authenticate(administrator(), client)
        return

    raise ValueError(f"Unknown user type: {user_type}")


def authenticate(username: str, client: TestClient) -> None:
    response = client.post(
        "/token", data={"username": username, "password": USER_PASSWORD}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


@given("I am not authenticated")
def i_am_not_authenticated(client: TestClient) -> None:
    not_authenticated(client)


def not_authenticated(client: TestClient) -> None:
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


@given(parsers.parse("I am an investigator for the proposal {proposal_code}"))
def i_am_investigator(proposal_code: str, client: TestClient) -> None:
    authenticate(investigator(proposal_code), client)


def investigator(proposal_code: str) -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["investigators"][proposal_code])


@given(parsers.parse("I am a Principal Investigator for the proposal {proposal_code}"))
def i_am_principal_investigator(proposal_code: str, client: TestClient) -> None:
    authenticate(principal_investigator(proposal_code), client)


def principal_investigator(proposal_code: str) -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["principal_investigators"][proposal_code])


@given(parsers.parse("I am a Principal Contact for the proposal {proposal_code}"))
def i_am_principal_contact(proposal_code: str, client: TestClient) -> None:
    authenticate(principal_contact(proposal_code), client)


def principal_contact(proposal_code: str) -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["principal_contacts"][proposal_code])


@given(parsers.parse("I am TAC chair for the partner {partner_code}"))
def i_am_tac_chair(partner_code: str, client: TestClient) -> None:
    authenticate(tac_chair(partner_code), client)


def tac_chair(partner_code: str) -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["tac_chairs"][partner_code])


@given(parsers.parse("I am a TAC member for the partner {partner_code}"))
def i_am_tac_member(partner_code: str, client: TestClient) -> None:
    authenticate(tac_chair(partner_code), client)


def tac_member(partner_code: str) -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["tac_members"][partner_code])


@given("I am a Board member")
def i_am_a_board_member(client: TestClient) -> None:
    authenticate(board_member(), client)


def board_member() -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["board_member"])


@given("I am a partner affiliated user")
def i_am_a_partner_affiliated_user(client: TestClient) -> None:
    authenticate(partner_affiliated_user(), client)


def partner_affiliated_user() -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["partner_affiliated_user"])


@given("I am a non-partner affiliated user")
def i_am_a_non_partner_affiliated_user(client: TestClient) -> None:
    authenticate(non_partner_affiliated_user(), client)


def non_partner_affiliated_user() -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["non_partner_affiliated_user"])


@given("I am a SALT Astronomer")
def i_am_a_salt_astronomer(client: TestClient) -> None:
    authenticate(salt_astronomer(), client)


def salt_astronomer() -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["salt_astronomer"])


@given("I am an administrator")
def i_am_an_administrator(client: TestClient) -> None:
    authenticate(administrator(), client)


def administrator() -> str:
    users = read_testdata(TEST_DATA)
    return cast(str, users["administrator"])


@then("this is OK")
def this_is_ok(response: Response) -> None:
    assert response.status_code == status.HTTP_200_OK


@then("I get an authentication error")
def authentication_error(response: Response) -> None:
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@then("I get a permission error")
def permission_error(response: Response) -> None:
    assert response.status_code == status.HTTP_403_FORBIDDEN
