import os.path as osp
from typing import Any

from fastapi import APIRouter, Depends, Path
from fastapi.responses import FileResponse

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.settings import get_settings
from saltapi.web import services

router = APIRouter(prefix="/finding-charts", tags=["Finding charts"])

finding_charts_directory = get_settings().finding_charts_dir


@router.get("/{finding_chart_id}", summary="Get a finding chart")
def get_finding_charts(
    finding_chart_id: int = Path(
        ..., title="Finding chart id", description="Unique identifier for finding chart"
    ),
    user: _User = Depends(get_current_user),
) -> Any:
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        finding_chart_service = services.finding_chart_service(unit_of_work.connection)

        [proposal_code, finding_chart_path] = finding_chart_service.get_finding_chart(
            finding_chart_id
        )

        permission_service.check_permission_to_view_proposal(user, proposal_code)

        filename = osp.join(finding_charts_directory, proposal_code, finding_chart_path)

        return FileResponse(filename)
