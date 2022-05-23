import os
import uuid

import dotenv
# Make sure that the test database etc. are used.
# IMPORTANT: These lines must be executed before any server-related package is imported.
import numpy as np

os.environ["DOTENV_FILE"] = ".env.test"
dotenv.load_dotenv(os.environ["DOTENV_FILE"])

from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, cast

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
from saltapi.web.schema.block import Block as _Block
from saltapi.web.schema.user import User as _User

engine: Optional[Engine] = None
sdb_dsn = os.environ.get("SDB_DSN")
if sdb_dsn:
    echo_sql = True if os.environ.get("ECHO_SQL") else False  # SQLAlchemy needs a bool
    engine = create_engine(sdb_dsn, echo=echo_sql, future=True)


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


@pytest.fixture()
def check_user(data_regression) -> Generator[Callable[[_User], None], None, None]:
    """
    Return a function for checking user details.
    In case you need to update the saved files, run ``pytest`` with the
    ``--force-regen`` flag.
    Parameters
    ----------
    data_regression: data regression fixture
        The data regression fixture from the pytest-regressions plugin.
    Returns
    -------
    function
        The function for checking user details.
    """

    def _check_user(user_details: _User) -> None:
        np.random.seed(0)
        try:
            data_regression.check(
                data_dict=user_details, basename="{}".format(dict(user_details)["id"])
            )
        finally:
            np.random.seed()

    yield _check_user


@pytest.fixture()
def check_block(data_regression) -> Generator[Callable[[_Block], None], None, None]:
    """
    Return a function for checking a block.
    In case you need to update the saved files, run ``pytest`` with the
    ``--force-regen`` flag.
    Parameters
    ----------
    data_regression: data regression fixture
        The data regression fixture from the pytest-regressions plugin.
    Returns
    -------
    function
        The function for checking a block.
    """

    def _check_block(block: _Block) -> None:
        np.random.seed(0)
        try:
            block_copy = dict(block).copy()
            block_copy["observing_conditions"]["maximum_lunar_phase"] = float(
                block_copy["observing_conditions"]["maximum_lunar_phase"]
            )
            block_copy["observing_conditions"]["minimum_lunar_distance"] = float(
                block_copy["observing_conditions"]["minimum_lunar_distance"]
            )
            for observations in block_copy["observations"]:
                for telescope_config in observations["telescope_configurations"]:
                    if telescope_config["dither_pattern"]:
                        telescope_config["dither_pattern"]["offset_size"] = float(
                            telescope_config["dither_pattern"]["offset_size"]
                        )
                    if telescope_config["guide_star"]:
                        telescope_config["guide_star"]["right_ascension"] = float(
                            telescope_config["guide_star"]["right_ascension"]
                        )
                        telescope_config["guide_star"]["declination"] = float(
                            telescope_config["guide_star"]["declination"]
                        )
            data_regression.check(
                data_dict=block_copy, basename="{}".format(block_copy["id"])
            )
        finally:
            np.random.seed()

    yield _check_block


@pytest.fixture()
def check_instrument(
    data_regression,
) -> Generator[Callable[[Dict[str, Any]], None], None, None]:
    """
    Return a function for checking an instrument.
    In case you need to update the saved files, run ``pytest`` with the
    ``--force-regen`` flag.
    Parameters
    ----------
    data_regression: data regression fixture
        The data regression fixture from the pytest-regressions plugin.
    Returns
    -------
    function
        The function for checking an instrument.
    """

    def _check_instrument(instrument: Dict[str, Any]) -> None:
        np.random.seed(0)
        try:
            if "iris_size" in instrument:
                instrument["iris_size"] = float(instrument["iris_size"])
            if "shutter_open_time" in instrument:
                instrument["shutter_open_time"] = float(instrument["shutter_open_time"])
            if "configuration" in instrument:
                if "fiber_separation" in instrument["configuration"]:
                    instrument["configuration"]["fiber_separation"] = float(
                        instrument["configuration"]["fiber_separation"]
                    )
                if (
                    "spectroscopy" in instrument["configuration"]
                    and instrument["configuration"]["spectroscopy"] is not None
                ):
                    if "grating_angle" in instrument["configuration"]["spectroscopy"]:
                        instrument["configuration"]["spectroscopy"][
                            "grating_angle"
                        ] = float(
                            instrument["configuration"]["spectroscopy"]["grating_angle"]
                        )

                if "mask" in instrument["configuration"]:
                    if instrument["configuration"]["mask"] is not None:
                        if "equinox" in instrument["configuration"]["mask"]:
                            instrument["configuration"]["mask"]["equinox"] = float(
                                instrument["configuration"]["mask"]["equinox"]
                            )
            if "detector" in instrument:
                instrument["detector"]["exposure_time"] = float(
                    instrument["detector"]["exposure_time"]
                )
            if "procedure" in instrument:
                if "blue_exposure_times" in instrument["procedure"]:
                    for i in range(len(instrument["procedure"]["blue_exposure_times"])):
                        instrument["procedure"]["blue_exposure_times"][i] = float(
                            instrument["procedure"]["blue_exposure_times"][i]
                        )

                if "red_exposure_times" in instrument["procedure"]:
                    for i in range(len(instrument["procedure"]["red_exposure_times"])):
                        instrument["procedure"]["red_exposure_times"][i] = float(
                            instrument["procedure"]["red_exposure_times"][i]
                        )

                if "exposures" in instrument["procedure"]:
                    for i in range(len(instrument["procedure"]["exposures"])):
                        instrument["procedure"]["exposures"][i][
                            "exposure_time"
                        ] = float(
                            instrument["procedure"]["exposures"][i]["exposure_time"]
                        )

                if "etalon_wavelengths" in instrument["procedure"]:
                    if instrument["procedure"]["etalon_wavelengths"] is not None:
                        for i in range(
                            len(instrument["procedure"]["etalon_wavelengths"])
                        ):
                            instrument["procedure"]["etalon_wavelengths"][i] = float(
                                instrument["procedure"]["etalon_wavelengths"][i]
                            )

            if "observation_time" in instrument:
                instrument["observation_time"] = float(instrument["observation_time"])

            if "overhead_time" in instrument:
                instrument["overhead_time"] = float(instrument["overhead_time"])

            if "exposure_time" in instrument:
                instrument["exposure_time"] = float(instrument["exposure_time"])

            if "arc_bible_entries" in instrument:
                if instrument["arc_bible_entries"] is not None:
                    for i in range(len(instrument["arc_bible_entries"])):
                        instrument["arc_bible_entries"][i][
                            "original_exposure_time"
                        ] = float(
                            instrument["arc_bible_entries"][i]["original_exposure_time"]
                        )
                        instrument["arc_bible_entries"][i][
                            "preferred_exposure_time"
                        ] = float(
                            instrument["arc_bible_entries"][i][
                                "preferred_exposure_time"
                            ]
                        )

            data_regression.check(
                data_dict=instrument, basename="{}".format(instrument["id"])
            )
        finally:
            np.random.seed()

    yield _check_instrument


def authenticate(username: str, client: TestClient) -> None:
    response = client.post(
        "/token", data={"username": username, "password": USER_PASSWORD}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


def not_authenticated(client: TestClient) -> None:
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


def misauthenticate(client: TestClient) -> None:
    client.headers["Authorization"] = "Bearer some_invalid_token"


def _random_string() -> str:
    return str(uuid.uuid4())[:8]


def create_user(client: TestClient) -> List[Any]:
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
    return [cast(int, response.json()["id"]), cast(str, response.json()["username"])]
