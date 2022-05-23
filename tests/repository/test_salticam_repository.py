from typing import Any, Callable, Dict

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.salticam_repository import SalticamRepository


def test_top_level_values(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    salticam_id = 393
    salticam_repository = SalticamRepository(db_connection)
    salticam = salticam_repository.get(salticam_id)

    assert "id" in salticam
    assert "minimum_signal_to_noise" in salticam
    assert "observation_time" in salticam
    assert "overhead_time" in salticam
    check_instrument(salticam)


@pytest.mark.parametrize("salticam_id", [1043, 590, 887])
def test_detector(
    salticam_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    salticam_repository = SalticamRepository(db_connection)
    salticam = salticam_repository.get(salticam_id)

    assert "detector" in salticam
    detector = salticam["detector"]

    assert "detector_windows" in detector
    windows = detector["detector_windows"]

    if windows is not None:
        for window in windows:
            assert "center_right_ascension" in window
            assert "center_declination" in window
            assert "height" in window
            assert "width" in window
    check_instrument(salticam)


def test_procedure(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    salticam_id = 1215
    salticam_repository = SalticamRepository(db_connection)
    salticam = salticam_repository.get(salticam_id)
    assert "procedure" in salticam
    check_instrument(salticam)
