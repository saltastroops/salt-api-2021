import os
import re
import pathlib
import uuid

import dotenv

# Make sure that the test database etc. are used.
# IMPORTANT: These lines must be executed before any server-related package is imported.

os.environ["DOTENV_FILE"] = ".env.test"
dotenv.load_dotenv(os.environ["DOTENV_FILE"])


from pathlib import Path
from typing import Any, Callable, Dict, Generator, Optional, cast

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

import saltapi.web.api.authentication
from saltapi.exceptions import NotFoundError
from saltapi.main import app
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import User
from saltapi.service.user_service import UserService

engine: Optional[Engine] = None
sdb_dsn = os.environ.get("SDB_DSN")
if sdb_dsn:
    echo_sql = True if os.environ.get("ECHO_SQL") else False  # SQLAlchemy needs a bool
    engine = create_engine(sdb_dsn, echo=echo_sql, future=True)


class PreviousDataFixture:
    def __init__(self, data_regression, request):
        self._data_regression = data_regression
        self._request = request

    def check(self, data_dict):
        # Find the directory and filename for the datafile
        cwd = pathlib.Path.cwd()
        filepath = Path(self._request.module.__file__)
        relative_filepath = filepath.relative_to(cwd)

        # We need a directory with the same name as the test file, but without the file
        # extension
        relative_data_dir = relative_filepath.parent / os.path.splitext(filepath.name)[0]
        base_data_dir = Path(os.environ["TEST_DATA_DIR"])
        data_dir = base_data_dir / relative_data_dir
        data_dir.mkdir(parents=True, exist_ok=True)

        # Get the filepath for the data file
        # Taken from pytest-datadir
        data_file_basename = re.sub(r"[\W]", "_", self._request.node.name)
        data_file = data_dir / f"{data_file_basename}.yml"
        self._data_regression.check(data_dict, fullpath=str(data_file))


@pytest.fixture()
def previous_data(data_regression, request):
    """
    Check a dict against previously saved version.

    The data will be stored in a subdirectory of the directory specified with the
    TEST_DATA_DIR environment variable.
    """
    yield PreviousDataFixture(data_regression, request)


def get_user_authentication_function() -> Callable[[str, str], User]:
    def authenticate_user(username: str, password: str) -> User:
        if password != USER_PASSWORD:
            raise NotFoundError("No user found for username and password")

        with cast(Engine, engine).connect() as connection:
            user_repository = UserRepository(connection)
            user_service = UserService(user_repository)
            user = user_service.get_user_by_username(username)
            return user

    return authenticate_user


app.dependency_overrides[
    saltapi.web.api.authentication.get_user_authentication_function
] = get_user_authentication_function


TEST_DATA = "users.yaml"


# Replace the user authentication with one which assumes that every user has the
# password "secret".

USER_PASSWORD = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_HOURS = 7 * 24


@pytest.fixture(scope="function")
def db_connection() -> Generator[Connection, None, None]:
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

    root_dir = Path(os.environ["TEST_DATA_DIR"])
    datafile = root_dir / path
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


def find_username(
    user_type: str,
    proposal_code: Optional[str] = None,
    partner_code: Optional[str] = None,
) -> str:
    """
    Find the username of a user who has a given user type.

    Depending on the user type, a proposal code or partner code must be supplied.
    """
    normalized_user_type = user_type.lower()
    normalized_user_type = normalized_user_type.replace(" ", "_").replace("-", "_")

    users = read_testdata(TEST_DATA)

    if normalized_user_type in [
        "investigator",
        "principal_investigator",
        "principal_contact",
    ]:
        if proposal_code is None:
            raise ValueError(f"Proposal code missing for user type {user_type}")
        return cast(str, users[normalized_user_type + "s"][proposal_code])

    if normalized_user_type in ["tac_chair", "tac_member"]:
        if partner_code is None:
            raise ValueError(f"Partner code missing for user type {user_type}")
        return cast(str, users[normalized_user_type + "s"][partner_code])

    if normalized_user_type in users:
        return cast(str, users[normalized_user_type])

    raise ValueError(f"Unknown user type: {user_type}")


def authenticate(username: str, client: TestClient) -> None:
    response = client.post(
        "/token", data={"username": username, "password": USER_PASSWORD}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


def get_authenticated_user_id(client: TestClient) -> int:
    response = client.get("/user")
    user = response.json()
    return cast(int, user["id"])


def not_authenticated(client: TestClient) -> None:
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


def misauthenticate(client: TestClient) -> None:
    client.headers["Authorization"] = "Bearer some_invalid_token"


def _random_string() -> str:
    return str(uuid.uuid4())[:8]


def create_user(client: TestClient) -> Dict[str, Any]:
    username = _random_string()
    new_user_details = dict(
        username=username,
        email=f"{username}@example.com",
        given_name=_random_string(),
        family_name=_random_string(),
        password="very_secret",
        institution_id=5,
    )
    response = client.post("/users/", json=new_user_details)
    return dict(response.json())
