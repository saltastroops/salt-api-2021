from typing import Dict, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from starlette import status

from saltapi.repository.database import engine
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.submissions import SubmissionIdentifier

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post(
    "/",
    summary="Submit a proposal",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SubmissionIdentifier,
)
async def create_submission(
    proposal: UploadFile = File(
        ..., title="Proposal", description="Zip file containing the proposal"
    ),
    proposal_code: Optional[str] = Query(
        None, alias="proposal-code", title="Proposal code", description="Proposal code"
    ),
    user: User = Depends(get_current_user),
) -> Dict[str, str]:
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
    # Submissions don't use database transactions. As such no unit of work is used.
    submission_repository = SubmissionRepository(engine.connect())
    submission_service = services.submission_service(submission_repository)
    submission_identifier = await submission_service.submit_proposal(
        user, proposal, proposal_code
    )
    return {"submission_identifier": submission_identifier}
