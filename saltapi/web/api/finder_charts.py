from typing import Any

from fastapi import APIRouter, Depends, Path
from fastapi.responses import FileResponse

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.web import services

router = APIRouter(prefix="/finder-charts", tags=["Finding charts"])


@router.get("/{finder_chart_id}", summary="Get a finding chart")
def get_finding_charts(
    finder_chart_id: int = Path(
        ..., title="Finder chart id", description="Unique identifier for a finder chart"
    ),
    user: _User = Depends(get_current_user),
) -> Any:
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        finding_chart_service = services.finder_chart_service(unit_of_work.connection)

        proposal_code, finder_chart_path = finding_chart_service.get_finder_chart(
            finder_chart_id
        )

        permission_service.check_permission_to_view_proposal(user, proposal_code)

        return FileResponse(finder_chart_path)
