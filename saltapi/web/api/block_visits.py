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
from saltapi.service.block import BlockVisit as _BlockVisit
from saltapi.service.block import BlockVisitStatus as _BlockVisitStatus
from saltapi.service.block_service import BlockService
from saltapi.service.permission_service import PermissionService
from saltapi.service.user import User
from saltapi.web.schema.common import BlockVisit, BlockVisitStatus

router = APIRouter(prefix="/block-visits", tags=["Block visit"])


def create_block_repository(connection: Connection) -> BlockRepository:
    return BlockRepository(
        target_repository=TargetRepository(connection),
        instrument_repository=InstrumentRepository(connection),
        connection=connection,
    )


@router.get("/{block_visit_id}", summary="Get a block visit", response_model=BlockVisit)
def get_block_visit(
    block_visit_id: int = Path(
        ..., title="Block visit id", description="Unique identifier for block visits"
    ),
    user: User = Depends(get_current_user),
) -> _BlockVisit:
    """
    Returns a block visit.

    A block visit is an observation which has been made for a block or which is in the
    queue to be observed.
    """
    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_view_block_visit(user, block_visit_id):
            block_service = BlockService(block_repository)
            block_visit = block_service.get_block_visit(block_visit_id)
            return block_visit

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.get(
    "/{block_visit_id}/status",
    summary="Get the status of a block visit",
    response_model=BlockVisitStatus,
)
def get_block_visit_status(
    block_visit_id: int = Path(
        ..., title="Block visit id", description="Unique identifier for a block visit"
    ),
    user: User = Depends(get_current_user),
) -> _BlockVisitStatus:
    """
    Returns the status of a block visit.

    The following status values are possible.

    Status | Description
    --- | ---
    Accepted | The observations are accepted.
    In queue | The observations are in a queue.
    Rejected | The observations are rejected.
    """
    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_view_block_visit(user, block_visit_id):
            block_service = BlockService(block_repository)
            return block_service.get_block_visit_status(block_visit_id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.put("/{block_visit_id}/status", summary="Update the status of a block visit")
def update_block_visit_status(
    block_visit_id: int = Path(
        ..., title="Block visit id", description="Unique identifier for a block visit"
    ),
    block_visit_status: BlockVisitStatus = Body(
        ...,
        alias="status",
        title="Block visit status",
        description="New block visit status.",
    ),
    user: User = Depends(get_current_user),
) -> None:
    """
    Updates the status of a block visit with the given the block visit id.
    See the corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = create_block_repository(unit_of_work.connection)
        permission_service = PermissionService(
            user_repository=UserRepository(unit_of_work.connection),
            proposal_repository=ProposalRepository(unit_of_work.connection),
            block_repository=block_repository,
        )
        if permission_service.may_update_block_visit_status(user):
            block_service = BlockService(block_repository)
            return block_service.update_block_visit_status(
                block_visit_id, block_visit_status
            )
