from typing import Any, Dict, Optional, cast

import pytest

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from saltapi.service.block import Block, BlockStatus, BlockVisitStatus
from saltapi.service.block_service import BlockService
from saltapi.web.schema.common import BlockRejectionReason


class FakeBlockRepository:
    def __init__(self) -> None:
        self.block_status = {"value": "Active", "reason": None}
        self.block_visit_status = {"status": "Rejected", "rejected_reason": None}

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

    def get_block_visit(self, block_visit_id: int) -> Dict[str, Any]:
        if block_visit_id == BLOCK_VISIT_ID:
            block_visit = {
                "id": BLOCK_VISIT_ID,
                "night": "2000-01-01",
                "status": self.block_visit_status["status"],
                "rejected_reason": self.block_visit_status["rejected_reason"],
            }
            return block_visit
        raise NotFoundError

    def get_block_status(self, block_id: int) -> BlockStatus:
        if block_id == VALID_BLOCK_ID:
            return self.block_status
        raise NotFoundError()

    def get_block_visit_status(self, block_visit_id: int) -> BlockVisitStatus:
        if block_visit_id == BLOCK_VISIT_ID:
            return self.block_visit_status
        raise NotFoundError()

    def update_block_status(
        self, block_id: int, value: str, reason: Optional[str]
    ) -> None:
        if block_id == VALID_BLOCK_ID:
            self.block_status = {"value": value, "reason": reason}
        else:
            raise NotFoundError()

    def update_block_visit_status(
        self, block_id: int, value: str, rejection_reason: Optional[str]
    ) -> None:
        if block_id == BLOCK_VISIT_ID:
            self.block_visit_status = {
                "status": value,
                "rejected_reason": rejection_reason,
            }
        else:
            raise NotFoundError()


BLOCK = {
    "id": 1,
    "semester": "2015-1",
    "status": {"value": "Completed", "reason": ""},
    "priority": 0,
    "ranking": "High",
}

BLOCK_VISIT = {
    "id": 2,
    "night": "2000-01-01",
    "status": "Rejected",
    "rejected_reason": None,
}


VALID_BLOCK_ID = 1
BLOCK_VISIT_ID = 2


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


def test_get_block_visit() -> None:
    block_service = create_block_service()
    block_visit = block_service.get_block_visit(BLOCK_VISIT_ID)

    assert BLOCK_VISIT == block_visit


def test_update_block_visit_status() -> None:
    block_service = create_block_service()

    old_status = block_service.get_block_visit_status(BLOCK_VISIT_ID)
    assert old_status != "Accepted"

    block_service.update_block_visit_status(BLOCK_VISIT_ID, "Accepted", None)

    new_status = block_service.get_block_visit_status(BLOCK_VISIT_ID)
    assert new_status["status"] == "Accepted"


def test_update_block_visit_status_and_rejection_reason() -> None:
    block_service = create_block_service()

    block_visit = block_service.get_block_visit(BLOCK_VISIT_ID)
    assert block_visit["status"] != "Not set"
    rejected_reason = BlockRejectionReason("Other").value
    block_service.update_block_visit_status(BLOCK_VISIT_ID, "Not set", rejected_reason)

    new_block_visit = block_service.get_block_visit(BLOCK_VISIT_ID)
    assert new_block_visit["status"] == "Not set"
    assert new_block_visit["rejected_reason"] == "Other"


def test_update_block_visit_status_raises_error_for_wrong_block_id() -> None:
    block_service = create_block_service()
    with pytest.raises(NotFoundError):
        block_service.update_block_visit_status(0, "In queue", None)
