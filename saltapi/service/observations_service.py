from typing import List, Dict, Any

from saltapi.repository.block_repository import BlockRepository
from saltapi.web.schema.block import BlockVisitStatus


class ObservationService:
    def __init__(self, block_repository: BlockRepository):
        self.block_repository = block_repository

    def get_observations(self, block_visit_id: int) -> List[Dict[str, Any]]:
        """
        Returns observations of a given block visit id.
        """

        return self.block_repository.get_observations(block_visit_id)

    def get_observations_status(self, block_visit_id: int) -> BlockVisitStatus:
        """
        Return the observation status for a block visit id.
        """

        return self.block_repository.get_observations_status(block_visit_id)

    def update_observations_status(self, block_visit_id: int, status: str) -> None:
        """
        Set the observation status for a block id.
        """

        return self.block_repository.update_observations_status(block_visit_id, status)
