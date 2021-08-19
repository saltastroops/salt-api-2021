from fastapi import APIRouter, Path, Body

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block import Block as _Block
from saltapi.web.schema.block import (
    Block,
    BlockStatus
)
router = APIRouter(prefix="/blocks", tags=["Block"])


@router.get("/{block_id}", summary="Get a block", response_model=Block)
def get_block(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    )
) -> _Block:
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


@router.get("/{block_id}/status", summary="Get a block status", response_model=BlockStatus)
def get_block_status(
        block_id: int = Path(
            ..., title="Block id", description="Unique identifier for the block"
        )
) -> BlockStatus:
    """
    Returns the status of the block with a given block id.

    The following status values are possible.

    Status | Description
    --- | ---
    Active | The block is active
    Completed | The block has been completed.
    Deleted | The block has been deleted.
    Expired | The proposal was submitted in a previous semester and will not be observed any longer.
    Not set | The block currently is not in the queue and will not be observed.
    On Hold | The block is currently on hold..
    Superseded | The block has been superseded. This is a legacy status that should not be used any longer.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        return block_repository.get_block_status(block_id)


@router.put("/{block_id}/status", summary="Update a block status", response_model=BlockStatus)
def update_block_status(
        block_id: int = Path(
            ..., title="Block id", description="Unique identifier for the block"
        ),
        block_status: BlockStatus = Body(
            ..., alias="status", title="Block status", description="New block status."
        ),
) -> BlockStatus:
    """
    Updates the status of the block with the given the block id. See the
    corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        return block_repository.update_block_status(block_id, block_status)

