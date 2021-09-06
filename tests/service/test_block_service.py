from typing import cast, Optional


from saltapi.repository.block_repository import BlockRepository
from saltapi.service.block import Block
from saltapi.service.block_service import BlockService


class FakeBlockRepository:
    def get(self, block_id) -> Optional[Block]:
        if block_id == 1:
            block = {"id": 1,
                     "semester": "2015-1",
                     "status": {"value": "Completed", "comment": ""},
                     "priority": 0,
                     "ranking": "High"}
            return block
        return None


block_repository = cast(BlockRepository, FakeBlockRepository())

block_id = 1


def test_get_block() -> None:
    block_service = BlockService(block_repository)
    block = block_service.get_block(block_id)

    assert "id" in block
    assert "semester" in block
    assert "status" in block


def test_get_block_status() -> None:
    block_service = BlockService(block_repository)
    block = block_service.get_block(block_id)
    assert block["status"]["value"] == "Completed"


def test_set_block_status() -> None:
    block_service = BlockService(block_repository)
    block = block_service.get_block(block_id)
    block["status"]["value"] = "In queue"
    assert block["status"]["value"] == "In queue"
