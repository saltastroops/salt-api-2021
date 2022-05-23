from typing import Any, Callable, Dict

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.hrs_repository import HrsRepository


def test_top_level_values(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    hrs_id = 639
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)
    print(hrs)
    assert "id" in hrs
    assert "observation_time" in hrs
    assert "overhead_time" in hrs
    check_instrument(hrs)


@pytest.mark.parametrize("hrs_id", [1358, 261, 1615])
def test_configuration(
    hrs_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)
    assert "configuration" in hrs
    check_instrument(hrs)


@pytest.mark.parametrize("hrs_id", [2319, 2298, 2320, 2327])
def test_mode(
    hrs_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)

    assert "configuration" in hrs
    assert "mode" in hrs["configuration"]
    check_instrument(hrs)


@pytest.mark.parametrize("hrs_id", [244, 2328, 1829])
def test_target_location(
    hrs_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)

    assert "target_location" in hrs["configuration"]
    check_instrument(hrs)


@pytest.mark.parametrize("hrs_id", [2297, 2320, 1615])
def test_iodine_cell_position(
    hrs_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)

    assert "iodine_cell_position" in hrs["configuration"]
    check_instrument(hrs)


@pytest.mark.parametrize("hrs_id", [2316, 80])
def test_detectors(
    hrs_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)

    assert "blue_detector" in hrs
    assert "red_detector" in hrs
    check_instrument(hrs)


def test_procedure(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    hrs_id = 385
    hrs_repository = HrsRepository(db_connection)
    hrs = hrs_repository.get(hrs_id)

    assert "procedure" in hrs
    check_instrument(hrs)
