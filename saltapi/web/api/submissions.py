from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile

from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post("/", summary="Submit a proposal")
def create_submission(
    proposal: UploadFile = File(
        ..., title="Proposal", description="Zip file containing the proposal"
    ),
    proposal_code: Optional[str] = Query(
        None, alias="proposal-code", title="Proposal code", description="Proposal code"
    ),
    user: User = Depends(get_current_user),
) -> None:
    """
    Submit a proposal.

    The proposal must be submitted as a zipfile containing the XML file defining the
    whole proposal or the updated/added blocks, as well as the additional files such as
    finder charts.

    A proposal code may be passed as a query parameter. This is mandatory when blocks
    rather than a whole proposal are submitted. If a whole proposal is submitted and a
    proposal code is supplied as a query parameter, the proposal code defined in the
    proposal must be the same as that passed as a query parameter.
    """
    with UnitOfWork() as unit_of_work:
        submission_repository = SubmissionRepository(unit_of_work.connection)
        submission_service = services.submission_service(submission_repository)
        submission_service.submit_proposal(user, proposal, proposal_code)
