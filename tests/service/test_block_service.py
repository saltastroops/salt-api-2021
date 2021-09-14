from typing import cast, Optional

import pytest

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from saltapi.service.block import Block, BlockStatus
from saltapi.service.block_service import BlockService


class FakeBlockRepository:
    def __init__(self) -> None:
        self.block_status = {"value": "Active", "reason": None}

    def get(self, block_id: int) -> Block:
        if block_id == VALID_BLOCK_ID:
            block = {
                "id": VALID_BLOCK_ID,
                "semester": "2015-1",
                "status": {"value": "Completed", "reason": ""},
                "priority": 0,
                "ranking": "High",
            }
            return block
        raise NotFoundError

    def get_block_status(self, block_id: int) -> BlockStatus:
        if block_id == VALID_BLOCK_ID:
            return self.block_status
        raise NotFoundError()

    def update_block_status(
        self, block_id: int, value: str, reason: Optional[str]
    ) -> None:
        if block_id == VALID_BLOCK_ID:
            self.block_status = {"value": value, "reason": reason}
        else:
            raise NotFoundError()


BLOCK = {
    "id": 1,
    "semester": "2015-1",
    "status": {"value": "Completed", "reason": ""},
    "priority": 0,
    "ranking": "High",
}


VALID_BLOCK_ID = 1


def create_block_service() -> BlockService:
    block_repository = cast(BlockRepository, FakeBlockRepository())
    return BlockService(block_repository)


def test_get_block() -> None:
    block_service = create_block_service()
    block = block_service.get_block(VALID_BLOCK_ID)

    assert BLOCK == block


def test_get_block_status_raises_error_for_wrong_block_id() -> None:
    block_service = create_block_service()
    with pytest.raises(NotFoundError):
        block_service.get_block(1234567)


def test_get_block_status() -> None:
    block_service = create_block_service()
    block = block_service.get_block(VALID_BLOCK_ID)
    status = block["status"]
    assert status["value"] == "Completed"
    assert status["reason"] == ""


def test_update_block_status() -> None:
    block_service = create_block_service()

    old_status = block_service.get_block_status(VALID_BLOCK_ID)
    assert old_status["value"] != "On hold"
    assert old_status["reason"] != "not needed"

    block_service.update_block_status(VALID_BLOCK_ID, "On hold", "not needed")

    new_status = block_service.get_block_status(VALID_BLOCK_ID)
    assert new_status["value"] == "On hold"
    assert new_status["reason"] == "not needed"


def test_update_block_status_raises_error_for_wrong_block_id() -> None:
    block_service = create_block_service()
    with pytest.raises(NotFoundError):
        block_service.update_block_status(0, "Active", "")
