from typing import Any, Callable, Dict

import pytest
from sqlalchemy.engine import Connection

from saltapi.repository.bvit_repository import BvitRepository


@pytest.mark.parametrize("bvit_id", [34, 75])
def test_bvit(
    bvit_id: int,
    db_connection: Connection,
    check_instrument: Callable[[Dict[str, Any]], None],
) -> None:
    bvit_repository = BvitRepository(db_connection)
    bvit = bvit_repository.get(bvit_id)

    assert "id" in bvit
    assert "mode" in bvit
    assert "filter" in bvit
    assert "neutral_density" in bvit
    assert "iris_size" in bvit
    assert "shutter_open_time" in bvit
    check_instrument(bvit)
