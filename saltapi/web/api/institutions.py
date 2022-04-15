from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.web import services
from saltapi.web.schema.institution import Affiliation

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get(
    "/",
    summary="Get a list of institutes",
    response_model=List[Affiliation],
)
def get_institutions(
    user: _User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with UnitOfWork() as unit_of_work:
        institution_service = services.institution_service(unit_of_work.connection)
        return institution_service.get_institutions()
