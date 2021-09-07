from typing import Dict

from fastapi import APIRouter, Path, Body, Depends, HTTPException
from starlette import status

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.user_repository import UserRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block import Block as _Block
from saltapi.service.permission_service import PermissionService
from saltapi.service.user import User
from saltapi.web.schema.block import (
    Block,
    BlockStatus
)
from saltapi.service.block_service import BlockService

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
        block_repository = BlockRepository(
            instrument_repository=InstrumentRepository(unit_of_work.connection),
            target_repository=TargetRepository(unit_of_work.connection),
            connection=unit_of_work.connection,
        )
        block_service = BlockService(block_repository)
        return block_service.get_block(block_id)


@router.get("/{block_id}/status", summary="Get a block status", response_model=Dict)
def get_block_status(
        block_id: int = Path(
            ..., title="Block id", description="Unique identifier for the block"
        )
) -> Dict:
    """
    Returns the status of the block with a given block id.

    The following status values are possible.

    Status | Description
    --- | ---
    Active | The block is active.
    Completed | The block has been completed.
    Deleted | The block has been deleted.
    Expired | The block was submitted in a previous semester and will not be observed any longer.
    Not set | The block currently is not set.
    On hold | The block status is currently on hold.
    Superseded | The block has been superseded. This is a legacy status that should not be used any longer.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = BlockRepository(
            instrument_repository=InstrumentRepository(unit_of_work.connection),
            target_repository=TargetRepository(unit_of_work.connection),
            connection=unit_of_work.connection,
        )
        block_service = BlockService(block_repository)
        return block_service.get_block_status(block_id)


@router.put("/{block_id}/status", summary="Update a block status", response_model=Block)
def update_block_status(
        block_id: int = Path(
            ..., title="Block id", description="Unique identifier for the block"
        ),
        block_status: BlockStatus = Body(
            ..., alias="status", title="Block status", description="New block status."
        ),
        user: User = Depends(),
) -> None:
    """
    Updates the status of the block with the given the block id.
    See the corresponding GET request for a description of the available status values.
    """
    try:
        with UnitOfWork() as unit_of_work:
            block_repository = BlockRepository(
                instrument_repository=InstrumentRepository(unit_of_work.connection),
                target_repository=TargetRepository(unit_of_work.connection),
                connection=unit_of_work.connection,
            )
            user_repository = UserRepository(unit_of_work.connection)
            block_service = BlockService(block_repository)
            permission_service = PermissionService(user_repository)
            if permission_service.may_update_proposal_status(user):
                return block_service.set_block_status(block_id, block_status)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
