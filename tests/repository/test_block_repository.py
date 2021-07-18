import json
from pathlib import Path
from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from tests.markers import nodatabase

TEST_DATA = "repository/block_repository.yaml"


@nodatabase
def test_get_block_returns_block_content(
    tmp_path: Path, dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    # set up fake block file
    data = testdata(TEST_DATA)["get"]
    block_id = data["block_id"]
    proposal_code = data["proposal_code"]
    block_code = data["block_code"]
    semester = data["semester"]
    included_dir = tmp_path / proposal_code / "Included"
    included_dir.mkdir(parents=True)
    block_file = included_dir / f"Block-{block_code}-{semester}.json"
    block_file_content = {"name": "Fake Block"}
    with open(block_file, "w") as f:
        json.dump(block_file_content, f)

    block_content = {}
    block_content.update(block_file_content)
    block_content["status"] = data["status"]
    block_content["observation_time"] = data["observation_time"]
    block_content["overhead_time"] = data["overhead_time"]
    block_content["probabilities"] = data["probabilities"]

    # check that the correct block content is returned
    block_repository = BlockRepository(dbconnection, tmp_path)
    assert block_repository.get(block_id) == block_content


@nodatabase
def test_get_raises_error_for_non_existing_block(
    tmp_path: Path, dbconnection: Connection
) -> None:
    block_repository = BlockRepository(dbconnection, tmp_path)
    with pytest.raises(NotFoundError):
        block_repository.get(1234567)
