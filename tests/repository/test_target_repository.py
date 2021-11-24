from decimal import Decimal
from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.target_repository import TargetRepository
from tests.markers import nodatabase

TEST_DATA = "repository/target_repository.yaml"


@nodatabase
def test_coordinates(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["coordinates"]
    for d in data:
        target_id = d["target_id"]
        expected_right_ascension = d["right_ascension"]
        expected_declination = d["declination"]
        expected_equinox = d["equinox"]
        target_repository = TargetRepository(dbconnection)
        target = target_repository.get(target_id)
        coordinates = target["coordinates"]

        assert pytest.approx(coordinates["right_ascension"]) == pytest.approx(
            expected_right_ascension
        )
        assert pytest.approx(coordinates["declination"]) == pytest.approx(
            expected_declination
        )
        assert coordinates["equinox"] == expected_equinox


@nodatabase
def test_no_coordinates(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_coordinates"]
    target_id = data["target_id"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)
    coordinates = target["coordinates"]

    assert coordinates is None


@nodatabase
def test_proper_motion(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["proper_motion"]
    target_id = data["target_id"]
    expected_motion = data["motion"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)
    motion = target["proper_motion"]

    assert pytest.approx(float(motion["right_ascension_speed"])) == pytest.approx(
        float(expected_motion["right_ascension_speed"])
    )
    assert pytest.approx(float(motion["declination_speed"])) == pytest.approx(
        float(expected_motion["declination_speed"])
    )
    assert motion["epoch"] == expected_motion["epoch"]


@nodatabase
def test_no_proper_motion(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_proper_motion"]
    for d in data:
        target_id = d["target_id"]
        target_repository = TargetRepository(dbconnection)
        target = target_repository.get(target_id)
        motion = target["proper_motion"]

        assert motion is None


@nodatabase
def test_magnitude(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["magnitude"]
    target_id = data["target_id"]
    expected_magnitude = data["magnitude"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)
    magnitude = target["magnitude"]

    assert magnitude == expected_magnitude


@nodatabase
def test_target_type(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["target_type"]
    for d in data:
        target_id = d["target_id"]
        expected_target_type = d["type"]
        target_repository = TargetRepository(dbconnection)
        target = target_repository.get(target_id)
        target_type = target["target_type"]

        assert target_type == expected_target_type


@nodatabase
def test_period_ephemeris(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["period_ephemeris"]
    target_id = data["target_id"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)
    ephemeris = target["period_ephemeris"]

    assert ephemeris["zero_point"] == Decimal(data["zero_point"])
    assert ephemeris["period"] == Decimal(data["period"])
    assert ephemeris["period_change_rate"] == Decimal(data["period_change_rate"])
    assert ephemeris["time_base"] == data["time_base"]


@nodatabase
def test_no_period_ephemeris(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_period_ephemeris"]
    target_id = data["target_id"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)
    ephemeris = target["period_ephemeris"]

    assert ephemeris is None


@nodatabase
def test_horizons_identifier(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["horizons_identifier"]
    for d in data:
        target_id = d["target_id"]
        expected_identifier = d["identifier"]
        target_repository = TargetRepository(dbconnection)
        target = target_repository.get(target_id)
        identifier = target["horizons_identifier"]

        assert identifier == expected_identifier


@nodatabase
def test_non_sidereal_target(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["non_sidereal_target"]
    target_id = data["target_id"]
    target_repository = TargetRepository(dbconnection)
    target = target_repository.get(target_id)

    assert target["horizons_identifier"] is None
    assert target["non_sidereal"] == 0


@nodatabase
def test_sidereal_target(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["sidereal_targets"]
    for d in data:
        target_id = d["target_id"]
        target_repository = TargetRepository(dbconnection)
        target = target_repository.get(target_id)
        expected_horizon_identifier = target["horizons_identifier"]
        expected_non_sidereal = target["non_sidereal"]

        assert d["identifier"] == expected_horizon_identifier
        assert d["non_sidereal"] == expected_non_sidereal
