from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.rss_repository import RssRepository
from tests.markers import nodatabase

TEST_DATA = "repository/rss_repository.yaml"


@nodatabase
def test_top_level_values(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["top_level_values"]
    rss_id = data["rss_id"]
    expected_rss = data["rss"]
    rss_repository = RssRepository(db_connection)
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
@nodatabase
def test_configuration(
    name: str, db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)[f"{name}_configuration"]
    rss_id = data["rss_id"]
    expected_config = data["configuration"]
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    config = rss["configuration"]

    assert config == expected_config


@nodatabase
def test_no_mask(db_connection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["no_mask"]
    rss_id = data["rss_id"]
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    mask = rss["configuration"]["mask"]

    assert mask is None


@nodatabase
def test_detector(db_connection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["detector"]
    for d in data:
        rss_id = d["rss_id"]
        expected_detector = d["detector"]
        rss_repository = RssRepository(db_connection)
        rss = rss_repository.get(rss_id)
        detector = rss["detector"]

        assert detector == expected_detector


@nodatabase
def test_detector_calculation(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["detector_calculations"]
    for d in data:
        rss_id = d["rss_id"]
        expected_calculation = d["calculation"]
        rss_repository = RssRepository(db_connection)
        rss = rss_repository.get(rss_id)
        calculation = rss["detector"]["detector_calculation"]

        assert calculation == expected_calculation


@nodatabase
def test_procedure_types(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["procedure_types"]
    for d in data:
        rss_id = d["rss_id"]
        expected_procedure_type = d["procedure_type"]
        rss_repository = RssRepository(db_connection)
        rss = rss_repository.get(rss_id)
        procedure_type = rss["procedure"]["procedure_type"]

        assert procedure_type == expected_procedure_type


@nodatabase
def test_procedure_etalon_pattern(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["procedure"]
    for d in data:
        rss_id = d["rss_id"]
        expected_procedure = d["procedure"]
        rss_repository = RssRepository(db_connection)
        rss = rss_repository.get(rss_id)
        procedure = rss["procedure"]

        if procedure["etalon_wavelengths"]:
            procedure["etalon_wavelengths"] = [
                float(w) for w in procedure["etalon_wavelengths"]
            ]

        assert procedure == expected_procedure


@nodatabase
def test_arc_bible_entries(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    # TODO: Add more test cases
    data = testdata(TEST_DATA)["arc_bible_entries"]
    rss_id = data["rss_id"]
    expected_arc_bible_entries = data["arc_bible_entries"]
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    arc_bible_entries = rss["arc_bible_entries"]

    assert len(arc_bible_entries) == len(expected_arc_bible_entries)
    for i in range(len(arc_bible_entries)):
        entry = arc_bible_entries[i]
        entry["original_exposure_time"] = float(entry["original_exposure_time"])
        entry["preferred_exposure_time"] = float(entry["preferred_exposure_time"])
        expected_entry = expected_arc_bible_entries[i]

        assert entry == expected_entry
