from typing import Any, Callable, Dict

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.rss_repository import RssRepository
from tests.markers import nodatabase


@nodatabase
def test_top_level_values(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    rss_id = 24293
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)

    assert "id" in rss
    assert "observation_time" in rss
    check_instrument(rss)


@nodatabase
@pytest.mark.parametrize("rss_id", [20792, 23573, 23472, 20708, 24087, 23231, 17823])
def test_configuration(
    rss_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)

    assert "configuration" in rss
    check_instrument(rss)


@nodatabase
def test_no_mask(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    rss_id = 13543
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)

    assert "configuration" in rss
    assert "mask" in rss["configuration"]
    assert rss["configuration"]["mask"] is None
    check_instrument(rss)


@nodatabase
@pytest.mark.parametrize("rss_id", [24190, 20934, 16604])
def test_detector(
    rss_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    assert "detector" in rss

    detector = rss["detector"]
    assert "mode" in detector
    assert "gain" in detector
    assert "iterations" in detector
    assert "detector_window" in detector
    check_instrument(rss)


@nodatabase
@pytest.mark.parametrize("rss_id", [20936, 23225, 24398, 24223])
def test_detector_calculation(
    rss_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)

    assert "detector" in rss
    assert "detector_calculation" in rss["detector"]
    check_instrument(rss)


@nodatabase
@pytest.mark.parametrize("rss_id", [20937, 20934, 20936, 24398, 23225, 24424, 24181])
def test_procedure_types(
    rss_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)

    assert "procedure" in rss
    assert "procedure_type" in rss["procedure"]
    check_instrument(rss)


@nodatabase
@pytest.mark.parametrize("rss_id", [17823, 24176])
def test_procedure_etalon_pattern(
    rss_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    procedure = rss["procedure"]

    assert "etalon_wavelengths" in procedure
    check_instrument(rss)


@nodatabase
def test_arc_bible_entries(
    db_connection: Connection, check_instrument: Callable[[Dict[str, Any]], None]
) -> None:
    # TODO: Add more test cases
    rss_id = 18294
    rss_repository = RssRepository(db_connection)
    rss = rss_repository.get(rss_id)
    print(rss)
    assert "arc_bible_entries" in rss
    arc_bible_entries = rss["arc_bible_entries"]

    for i in range(len(arc_bible_entries)):
        entry = arc_bible_entries[i]
        assert "original_exposure_time" in entry
        assert "preferred_exposure_time" in entry
    check_instrument(rss)
