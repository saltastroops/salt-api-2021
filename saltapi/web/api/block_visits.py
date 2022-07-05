from typing import Optional

from fastapi import APIRouter, Body, Depends, Path

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.block import BlockVisit as _BlockVisit
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.common import (
    BaseBlockVisit,
    BlockRejectionReason,
    BlockVisitStatusValue,
)

router = APIRouter(prefix="/block-visits", tags=["Block visit"])


@router.get(
    "/{block_visit_id}", summary="Get a block visit", response_model=BaseBlockVisit
)
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
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_block_visit(user, block_visit_id)

        block_service = services.block_service(unit_of_work.connection)
        block_visit = block_service.get_block_visit(block_visit_id)
        return block_visit


@router.patch("/{block_visit_id}/status", summary="Update the status of a block visit")
def update_block_visit_status(
    block_visit_id: int = Path(
        ..., title="Block visit id", description="Unique identifier for a block visit"
    ),
    block_visit_status: BlockVisitStatusValue = Body(
        ...,
        alias="status",
        title="Block visit status",
        description="New block visit status.",
    ),
    rejection_reason: Optional[BlockRejectionReason] = Body(
        None,
        alias="reason",
        title="Block visit rejection reason",
        description="New block visit rejection reason.",
    ),
    user: User = Depends(get_current_user),
) -> None:
    """
    Updates the status of a block visit with the given the block visit id.
    The following status and rejection_reason values are accepted.

    Status | Description
    --- | ---
    Accepted | The observations are accepted.
    In queue | The observations are in a queue.
    Rejected | The observations are rejected.

    Rejection reason
    ---
    Instrument technical problems
    Observing conditions not met
    Phase 2 problems
    Telescope technical problems
    Other
    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_block_visit_status(user)

        block_service = services.block_service(unit_of_work.connection)
        return block_service.update_block_visit_status(
            block_visit_id, block_visit_status, rejection_reason
        )
