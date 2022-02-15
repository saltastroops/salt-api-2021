from typing import Optional, List

from fastapi import APIRouter, Body, Depends, Query

from saltapi.service.authentication_service import get_current_user
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.user import User
from saltapi.web.schema.common import Semester
from saltapi.web import services
from saltapi.web.schema.mos import MosBlock

router = APIRouter(tags=["MosBlock"])


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
        mos_data = mos_service.get_mos_data(semesters)
        return [MosBlock(**md) for md in mos_data]
