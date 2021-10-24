from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.engine import Connection
from starlette import status

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.block import Block as _Block
from saltapi.service.block import BlockStatus as _BlockStatus
from saltapi.service.block_service import BlockService
from saltapi.service.permission_service import PermissionService
from saltapi.service.user import User
from saltapi.web.schema.block import Block, BlockStatus, BlockStatusValue

router = APIRouter(prefix="/blocks", tags=["Block"])


def create_block_repository(connection: Connection) -> BlockRepository:
    return BlockRepository(
        target_repository=TargetRepository(connection),
        instrument_repository=InstrumentRepository(connection),
        connection=connection,
    )


@router.get("/{block_id}", summary="Get a block", response_model=Block)
def get_block(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    user: User = Depends(get_current_user),
) -> _Block:
    """
    Returns the block with a given id.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_view_block(user, block_id):
            block_service = BlockService(block_repository)
            return block_service.get_block(block_id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.get(
    "/{block_id}/status", summary="Get a block status", response_model=BlockStatus
)
def get_block_status(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    user: User = Depends(get_current_user),
) -> _BlockStatus:
    """
    Returns the status of the block with a given block id.

    The status is described by a status value and a reason for that value.
    The following status values are possible.

    Status | Description
    --- | ---
    Active | The block is active.
    Completed | The block has been completed.
    Deleted | The block has been deleted.
    Expired | The block was submitted in a previous semester and will not be observed any longer.
    Not set | The block status currently is not set.
    On hold | The block is currently on hold.
    Superseded | The block has been superseded. This is a legacy status that should not be used any longer.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_view_block(user, block_id):
            block_service = BlockService(block_repository)
            return block_service.get_block_status(block_id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.put(
    "/{block_id}/status", summary="Update a block status", response_model=BlockStatus
)
def update_block_status(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    block_status: BlockStatusValue = Body(
        ..., alias="status", title="Block status", description="New block status."
    ),
    status_reason: str = Body(
        ...,
        alias="reason",
        title="Block status reason",
        description="New block status reason.",
    ),
    user: User = Depends(),
) -> _BlockStatus:
    """
    Updates the status of the block with the given the block id.
    See the corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_update_proposal_status(user):
            block_service = BlockService(block_repository)
            block_service.update_block_status(block_id, block_status, status_reason)

            return block_service.get_block_status(block_id)
