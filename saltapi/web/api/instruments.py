from typing import List
from fastapi import APIRouter, Depends

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services


router = APIRouter(prefix="/instruments", tags=["Instrument"])


@router.get(
    "/rss/current-mos-mask",
    summary="Get current MOS masks in the magazine",
    response_model=List[str]
)
def get_current_mos_mask(
    user: User = Depends(get_current_user),
) -> List[str]:
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
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_mos_data(user)

        instrument_service = services.instrument_service(unit_of_work.connection)
        return instrument_service.get_mos_mask_in_magazine()