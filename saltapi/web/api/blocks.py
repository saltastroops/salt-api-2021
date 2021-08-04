from typing import Any

from fastapi import Query, APIRouter

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block import Block


router = APIRouter(prefix="/blocks", tags=["Block"])


@router.get("/{block_id}", summary="Get a block", response_model=Any)
def get_block(
    block_id: int = Query(
        ..., title="Block id", description="Unique identifier for the block"
    )
) -> Block:
    """
    Returns the block with a given id.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        return block_repository.get(block_id)
