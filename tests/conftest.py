from pathlib import Path
from typing import Any, Callable

import pytest
import yaml


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

        tests_dir = Path(__file__).parent
        datafile = tests_dir / "testdata" / path
        if not datafile.exists():
            raise IOError(f"File does not exist: {datafile}")

        with open(datafile, "r") as f:
            return yaml.safe_load(f)

    yield _read_data
