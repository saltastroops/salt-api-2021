from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.rss_repository import RssRepository

TEST_DATA = "repository/rss_repository.yaml"


def test_id_name_cycles_times(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["id_name_cycles_times"]
    rss_id = data["rss_id"]
    expected_rss = data["rss"]
    rss_repository = RssRepository(dbconnection)
    rss = rss_repository.get(rss_id)

    assert rss["id"] == rss_id
    assert rss["name"] == "RSS"
    assert rss["cycles"] == expected_rss["cycles"]
    assert float(rss["observation_time"]) == expected_rss["observation_time"]
    assert float(rss["overhead_time"]) == expected_rss["overhead_time"]


@pytest.mark.parametrize(
    "name",
    [
        "imaging",
        "polarimetric_imaging",
        "spectroscopy",
        "spectropolarimetry",
        "mos",
        "mos_polarimetry",
        "fabry_perot",
    ],
)
def test_configuration(
    name: str, dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)[f"{name}_configuration"]
    rss_id = data["rss_id"]
    expected_config = data["configuration"]
    rss_repository = RssRepository(dbconnection)
    rss = rss_repository.get(rss_id)
    config = rss["configuration"]

    assert config == expected_config
