from typing import cast

import pytest
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from saltapi.service.block import Block
from saltapi.service.block_service import BlockService


class FakeBlockRepository:
    def get(self, block_id) -> Block:
        if block_id == 1:
            block = {"id": 1,
                     "semester": "2015-1",
                     "status": {"value": "Completed", "reason": ""},
                     "priority": 0,
                     "ranking": "High"}
            return block
        raise NotFoundError


block_repository = cast(BlockRepository, FakeBlockRepository())

BLOCK = {"id": 1,
         "semester": "2015-1",
         "status": {"value": "Completed", "reason": ""},
         "priority": 0,
         "ranking": "High"}


block_id = 1


def test_get_block() -> None:
    block_service = BlockService(block_repository)
    block = block_service.get_block(block_id)

    assert BLOCK == block


def test_get_block_status_raises_error_for_wrong_block_id() -> None:
    block_service = BlockService(block_repository)
    with pytest.raises(NotFoundError):
        block_service.get_block(1234567)


def test_get_block_status() -> None:
    block_service = BlockService(block_repository)
    block = block_service.get_block(block_id)
    status = block["status"]
    assert status["value"] == "Completed"
    assert status["reason"] == ""


def test_update_block_status() -> None:
    block_service = BlockService(block_repository)
    block_service.update_block_status(block_id, "On hold", "not needed")

    status = block_service.get_block_status(block_id)
    assert status["value"] == "On hold"
    assert status["reason"] == "not needed"


def test_update_block_status_raises_error_for_wrong_block_id() -> None:
    block_service = BlockService(block_repository)
    with pytest.raises(NoResultFound):
        block_service.update_block_status(0, "Active", "")


