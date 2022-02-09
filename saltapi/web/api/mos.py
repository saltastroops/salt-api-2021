from typing import Optional

from fastapi import Path, APIRouter, Body, Depends

from saltapi.service.authentication_service import get_current_user
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.user import User
from saltapi.web.schema.common import Semester
from saltapi.web import services
from saltapi.web.schema.mos import MosData

router = APIRouter(tags=["MosData"])


@router.post(
    "/mos",
    summary="Get MOS ata",
    response_model=MosData,
    status_code=200,
)
def get_mos_data(
    user: User = Depends(get_current_user),
    semester: Semester = Body(..., title="Semester", description="Semester"),
    include_next_semester: Optional[bool] = Body(..., title="Next semester", description="Is next semester included"),
    include_previous_semester: Optional[bool] = Body(..., title="Previous semester", description="Is previous semester included."),
) -> MosData:
    """
    Get MOS data.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_mos_data(
            user
        )

        mos_service = services.mos_service(unit_of_work.connection)
        mos_data = mos_service.get_mos_data(
            semester, include_next_semester, include_previous_semester
        )
        unit_of_work.connection.commit()
        return MosData(**mos_data)
