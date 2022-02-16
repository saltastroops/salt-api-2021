from typing import List
from fastapi import APIRouter, Depends

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services


router = APIRouter(tags=["Instrument"])


@router.get(
    "/rss/current-mos-masks",
    summary="Get current MOS masks in the magazine",
    response_model=List[str]
)
def get_current_mos_masks(
    user: User = Depends(get_current_user),
) -> List[str]:
    """
    Returns the list of MOS masks that are currently on the magazine.
    """

    with UnitOfWork() as unit_of_work:
        instrument_service = services.instrument_service(unit_of_work.connection)
        return instrument_service.get_mos_mask_in_magazine()