from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.salticam_repository import SalticamRepository

TEST_DATA = "repository/salticam_repository.yaml"


def test_top_level_values(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["top_level_values"]
    expected_salticam = data["salticam"]
    salticam_id = data["salticam_id"]
    salticam_repository = SalticamRepository(dbconnection)
    salticam = salticam_repository.get(salticam_id)

    assert salticam["id"] == salticam_id
    assert (
        salticam["minimum_signal_to_noise"]
        == expected_salticam["minimum_signal_to_noise"]
    )
    assert salticam["observation_time"] == expected_salticam["observation_time"]
    assert salticam["overhead_time"] == expected_salticam["overhead_time"]


def test_detector(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["detector"]
    for d in data:
        salticam_id = d["salticam_id"]
        expected_detector = d["detector"]
        salticam_repository = SalticamRepository(dbconnection)
        salticam = salticam_repository.get(salticam_id)
        detector = salticam["detector"]

        # detector windows must be compared separately
        expected_windows = expected_detector["detector_windows"]
        windows = detector["detector_windows"]
        if windows is not None:
            assert len(windows) == len(expected_windows)
            for i in range(len(windows)):
                assert pytest.approx(
                    float(windows[i]["center_right_ascension"])
                ) == pytest.approx(expected_windows[i]["center_right_ascension"])
                assert pytest.approx(
                    float(windows[i]["center_declination"])
                ) == pytest.approx(expected_windows[i]["center_declination"])
                assert windows[i]["height"] == expected_windows[i]["height"]
                assert windows[i]["width"] == expected_windows[i]["width"]
        else:
            assert expected_windows is None
        del expected_detector["detector_windows"]
        del detector["detector_windows"]

        assert detector == expected_detector


def test_procedure(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["procedure"]
    salticam_id = data["salticam_id"]
    expected_procedure = data["procedure"]
    salticam_repository = SalticamRepository(dbconnection)
    salticam = salticam_repository.get(salticam_id)
    procedure = salticam["procedure"]

    assert procedure == expected_procedure
