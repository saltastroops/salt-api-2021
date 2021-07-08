import os

import dotenv

# Make sure that the test database etc. are used.
# IMPORTANT: These lines must be executed before any server-related package is imported.

os.environ["DOTENV_FILE"] = ".env.test"
dotenv.load_dotenv(os.environ["DOTENV_FILE"])


from pathlib import Path
from typing import Any, Callable, Optional

import pytest
import yaml

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine


engine: Optional[Engine]
sdb_dsn = os.environ.get("SDB_DSN")
if sdb_dsn:
    echo_sql = True if os.environ.get("ECHO_SQL") else False  # SQLAlchemy needs a bool
    engine = create_engine(sdb_dsn, echo=True, future=True)


@pytest.fixture(scope="function")
def dbconnection() -> Connection:
    with engine.connect() as connection:
        yield connection


@pytest.fixture(scope="session")
def testdata() -> Callable[[str], Any]:
    """
    Load test data from a YAML file.

    The test data must be contained in a YAML file located in the folder tests/testdata
    or any subfolder thereof. The file path relative to the tests/testdata folder must
    be passed as the argument of the function returned by this fixture.

    The YAML file must contain a single document only (i.e. it must contain no "---"
    separators). Its content is returned in the way PyYAML returns YAML content.
    """

    def _read_data(path: str) -> Any:
        if Path(path).is_absolute():
            raise ValueError("The file path must be a relative path.")

        root_dir = Path(__file__).parent.parent
        datafile = root_dir / "testdata" / path
        if not datafile.exists():
            raise IOError(f"File does not exist: {datafile}")

        with open(datafile, "r") as f:
            return yaml.safe_load(f)

    yield _read_data
