from saltapi.repository.block_repository import BlockRepository


class ObservationService:
    def __init__(self, block_repository: BlockRepository):
        self.block_repository = block_repository

    def get_observations_status(self, block_visit_id: int) -> str:
        """
        Return the block content for a block id.
        """

        return self.block_repository.get_observations_status(block_visit_id)

    def set_observations_status(self, block_visit_id: int, status: str) -> str:
        """
        Return the block content for a block id.
        """

        return self.block_repository.update_observations_status(block_visit_id, status)