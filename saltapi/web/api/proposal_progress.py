from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.common import ProposalCode, Semester
from saltapi.web.schema.proposal import ProposalProgress

router = APIRouter(prefix="/progress", tags=["Proposals"])


@router.get(
    "/{proposal_code}/{semester}",
    summary="Get a proposal progress report",
    response_model=ProposalProgress,
    responses={200: {"content": {"application/pdf": {}}}},
)
def get_proposal_progress_report(
    proposal_code: ProposalCode = Path(
        ...,
        title="Proposal code",
        description="Proposal code of the proposal whose progress report is requested.",
    ),
    semester: Semester = Path(..., title="Semester", description="Semester"),
    user: User = Depends(get_current_user),
) -> ProposalProgress:
    """
    Returns the progress report for a proposal and semester. The semester is the
    semester for which the progress is reported. For example, if the semester is
    2021-1, the report covers the observations up to and including the 2021-1
    semester, and it requests time for the 2021-2 semester.

    The proposal progress report is returned as a JSON string, and it does not include the
    additional file uploaded by the user when creating the report. There is another
    endpoint for returning the report as a pdf, including the additional file and the
    original scientific justification.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_proposal(user, proposal_code)

        proposal_service = services.proposal_service(unit_of_work.connection)
        proposal_progress_report = proposal_service.get_progress_report(
            proposal_code, semester
        )
        return ProposalProgress(**proposal_progress_report)


@router.put(
    "/{proposal_code}/{semester}",
    summary="Create or update a progress report",
)
def put_progress_report(
    proposal_code: ProposalCode = Path(
        ...,
        title="Proposal code",
        description="Proposal code of the proposal whose progress report is created or"
        " updated.",
    ),
    semester: Semester = Path(..., title="Semester", description="Semester"),
    progress_report: ProposalProgress = Body(
        ..., title="Progress report", description="Progress report for a proposal."
    ),
    file: Optional[UploadFile] = File(...),
    user: User = Depends(get_current_user),
) -> ProposalProgress:
    """
    Creates or updates the progress report for a proposal and semester. The semester
    is the semester for which the progress is reported. For example, if the semester
    is 2021-1, the report covers the observations up to and including the 2021-1
    semester and it requests time for the 2021-2 semester.

    The optional pdf file is intended for additional details regarding the progress with
    the proposal.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_proposal(user, proposal_code)

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
