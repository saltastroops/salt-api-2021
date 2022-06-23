from typing import Optional

from fastapi import (
    Path,
    Depends,
    APIRouter,
    Body,
    UploadFile,
    File,
    HTTPException,
    status
)

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web.schema.common import Semester, ProposalCode
from saltapi.web.schema.proposal import ProposalProgress, ProgressReportData
from saltapi.web import services


router = APIRouter(prefix="/progress", tags=["Proposals"])


@router.get(
    "/{proposal_code}/{semester}",
    summary="Get a progress report",
    response_model=Optional[ProposalProgress],
    responses={200: {"content": {"application/pdf": {}}}},
)
def get_progress_report(
    proposal_code: ProposalCode = Path(
        ...,
        title="Proposal code",
        description="Proposal code of the proposal whose progress report is requested.",
    ),
    semester: Semester = Path(..., title="Semester", description="Semester"),
    user: User = Depends(get_current_user)
) -> ProposalProgress:
    """
    Returns the progress report for a proposal and semester. The semester is the
    semester for which the progress is reported. For example, if the semester is
    2021-1, the report covers the observations up to and including the 2021-1
    semester and it requests time for the 2021-2 semester.

    The progress report can be requested in either of two formats:

    * As a JSON string.
    * As a pdf file. This is the default.

    You can choose the format by supplying its content type in the `Accept` HTTP header:

    Returned object | `Accept` HTTP header value
    --- | ---
    JSON string | application/json
    pdf file | application/pdf

    A pdf file is returned if no `Accept` header is included in the request. In the
    case of the pdf file the response contains an `Content-Disposition` HTTP header
    with a filename of the form "ProgressReport_{proposal_code}_{semester}.pdf".
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_proposal(user, proposal_code)

        proposal_service = services.proposal_service(unit_of_work.connection)
        progress_report = proposal_service.get_progress_report(proposal_code, semester)
        return ProposalProgress(
            **progress_report
        )


@router.put(
    "/{proposal_code}/{semester}",
    summary="Create or update a progress report",
    response_model=ProposalProgress,
)
def put_progress_report(
    proposal_code: ProposalCode = Path(
        ...,
        title="Proposal code",
        description="Proposal code of the proposal whose progress report is created or"
                    " updated.",
    ),
    semester: Semester = Path(..., title="Semester", description="Semester"),
    progress_report: ProgressReportData = Body(
        ...,
        title="Progress report",
        description="Progress report for a proposal."
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

    # TODO Ask about what to do with the requested times for partners?
    # * how to add the requested times correctly to the database.
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_proposal(user, proposal_code)

        proposal_service = services.proposal_service(unit_of_work.connection)



    # TODO Save the pdfs. Both the supplementary PDF and the newly created file.
    # * Where to save the created files.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
