from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.rss_repository import RssRepository

TEST_DATA = "repository/rss_repository.yaml"


def test_top_level_values(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["top_level_values"]
    rss_id = data["rss_id"]
    expected_rss = data["rss"]
    rss_repository = RssRepository(dbconnection)
    rss = rss_repository.get(rss_id)

    assert rss["id"] == rss_id
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


def test_no_mask(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["no_mask"]
    rss_id = data["rss_id"]
    rss_repository = RssRepository(dbconnection)
    rss = rss_repository.get(rss_id)
    mask = rss["configuration"]["mask"]

    assert mask is None


def test_detector(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["detector"]
    for d in data:
        rss_id = d["rss_id"]
        expected_detector = d["detector"]
        rss_repository = RssRepository(dbconnection)
        rss = rss_repository.get(rss_id)
        detector = rss["detector"]

        assert detector == expected_detector


def test_detector_calculation(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["detector_calculations"]
    for d in data:
        rss_id = d["rss_id"]
        expected_calculation = d["calculation"]
        rss_repository = RssRepository(dbconnection)
        rss = rss_repository.get(rss_id)
        calculation = rss["detector"]["detector_calculation"]

        assert calculation == expected_calculation


def test_procedure_etalon_pattern(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["procedure"]
    for d in data:
        rss_id = d["rss_id"]
        expected_procedure = d["procedure"]
        rss_repository = RssRepository(dbconnection)
        rss = rss_repository.get(rss_id)
        procedure = rss["procedure"]

        if procedure["etalon_wavelengths"]:
            procedure["etalon_wavelengths"] = [
                float(w) for w in procedure["etalon_wavelengths"]
            ]

        assert procedure == expected_procedure
