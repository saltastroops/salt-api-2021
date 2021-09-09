from typing import Dict, Any

from saltapi.repository.block_repository import BlockRepository
from saltapi.service.block import Block


class BlockService:
    def __init__(self, block_repository: BlockRepository):
        self.block_repository = block_repository

    def get_block(self, block_id: int) -> Block:
        """
        Return the block content for a block id.
        """

        return self.block_repository.get(block_id)

    def get_block_status(self, block_id: int) -> Dict[str, Any]:
        """
        Return the block status for a block id.
        """

        return self.block_repository.get_block_status(block_id)

    def update_block_status(self, block_id: int, status: str, reason: str) -> None:
        """
        Set the block status for a block id.
        """

        return self.block_repository.update_block_status(block_id, status, reason)
