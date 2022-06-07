from typing import Any, Callable

from sqlalchemy.engine import Connection

from saltapi.repository.bvit_repository import BvitRepository

TEST_DATA = "repository/bvit_repository.yaml"


def test_hrs(db_connection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["bvit"]
    for d in data:
        bvit_id = d["bvit_id"]
        expected_bvit = d["bvit"]
        bvit_repository = BvitRepository(db_connection)
        bvit = bvit_repository.get(bvit_id)

        assert bvit["id"] == bvit_id
        assert bvit["mode"] == expected_bvit["mode"]
        assert bvit["filter"] == expected_bvit["filter"]
        assert bvit["neutral_density"] == expected_bvit["neutral_density"]
        assert bvit["iris_size"] == expected_bvit["iris_size"]
        assert bvit["shutter_open_time"] == expected_bvit["shutter_open_time"]
