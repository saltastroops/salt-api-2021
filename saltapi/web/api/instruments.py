from typing import List
from fastapi import APIRouter, Depends, Query

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.common import Semester
from saltapi.web.schema.rss import MosBlock

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

@router.get(
    "/mos",
    summary="Get MOS data",
    response_model=List[MosBlock],
    status_code=200,
)
def get_mos_data(
    user: User = Depends(get_current_user),
    semesters: List[Semester] = Query(..., title="Semester", description="Semester"),
) -> List[MosBlock]:
    """
    Get the list of blocks using MOS.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_mos_data(user)

        mos_service = services.mos_service(unit_of_work.connection)
        mos_data = mos_service.get_mos_data([str(s) for s in semesters])
        return [MosBlock(**md) for md in mos_data]