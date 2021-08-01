from typing import Any, Callable

from sqlalchemy.engine import Connection

from saltapi.repository.hrs_repository import HrsRepository

TEST_DATA = "repository/hrs_repository.yaml"


def test_top_level_values(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["top_level_values"]
    hrs_id = data["hrs_id"]
    expected_hrs = data["hrs"]
    hrs_repository = HrsRepository(dbconnection)
    hrs = hrs_repository.get(hrs_id)

    assert hrs["id"] == hrs_id
    assert hrs["name"] == "HRS"
    assert hrs["observation_time"] == expected_hrs["observation_time"]
    assert hrs["overhead_time"] == expected_hrs["overhead_time"]


def test_configuration(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["configuration"]
    for d in data:
        hrs_id = d["hrs_id"]
        expected_configuration = d["configuration"]
        hrs_repository = HrsRepository(dbconnection)
        hrs = hrs_repository.get(hrs_id)
        configuration = hrs["configuration"]

        assert configuration == expected_configuration


def test_mode(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["mode"]
    for d in data:
        hrs_id = d["hrs_id"]
        expected_mode = d["mode"]
        hrs_repository = HrsRepository(dbconnection)
        hrs = hrs_repository.get(hrs_id)
        mode = hrs["configuration"]["mode"]

        assert mode == expected_mode


def test_target_location(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["target_location"]
    for d in data:
        hrs_id = d["hrs_id"]
        expected_location = d["location"]
        hrs_repository = HrsRepository(dbconnection)
        hrs = hrs_repository.get(hrs_id)
        location = hrs["configuration"]["target_location"]

        assert location == expected_location


def test_iodine_cell_position(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["iodine_cell_position"]
    for d in data:
        hrs_id = d["hrs_id"]
        expected_position = d["position"]
        hrs_repository = HrsRepository(dbconnection)
        hrs = hrs_repository.get(hrs_id)
        position = hrs["configuration"]["iodine_cell_position"]

        assert position == expected_position


def test_detectors(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["detectors"]
    for d in data:
        hrs_id = d["hrs_id"]
        expected_blue_detector = d["blue_detector"]
        expected_red_detector = d["red_detector"]
        hrs_repository = HrsRepository(dbconnection)
        hrs = hrs_repository.get(hrs_id)
        blue_detector = hrs["blue_detector"]
        red_detector = hrs["red_detector"]

        assert blue_detector == expected_blue_detector
        assert red_detector == expected_red_detector


def test_procedure(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["procedure"]
    hrs_id = data["hrs_id"]
    expected_procedure = data["procedure"]
    hrs_repository = HrsRepository(dbconnection)
    hrs = hrs_repository.get(hrs_id)
    procedure = hrs["procedure"]

    assert procedure == expected_procedure
