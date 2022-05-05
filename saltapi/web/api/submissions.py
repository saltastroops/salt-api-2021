import asyncio
from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Path,
    Query,
    UploadFile,
    WebSocket,
)
from starlette import status

from saltapi.exceptions import NotFoundError
from saltapi.repository.database import engine
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import (
    find_user_from_token,
    get_current_user,
)
from saltapi.service.submission import SubmissionStatus
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.submissions import SubmissionIdentifier

router = APIRouter(prefix="/submissions", tags=["Submissions"])

TIME_BETWEEN_DB_QUERIES = 5


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
    proposal_code: Optional[str] = Form(
        None, title="Proposal code", description="Proposal code"
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


@router.websocket("/{identifier}/progress/ws")
async def submission_progress(
    websocket: WebSocket,
    identifier: str = Path(
        ...,
        title="Submission identifier",
        description="Unique identifier for the submission whose log is requested.",
    ),
    from_entry_number: int = Query(
        1,
        alias="from-entry-number",
        title="Minimum entry number",
        description="Minimum entry number from which onwards log entries are considered",
    ),
) -> None:
    """
    Request to receive the existing and all future log entries and status changes.

    After connecting to this endpoint you must send a message with a valid JWT token
    authenticating you. This is a token returned by the `/token` endpoint, as you would
    use in the `Authorization` header for other (HTTP) endpoints. If the token sent is
    invalid, the connection is closed with the closing code 1011.

    You must have created a submission in order to view its log or status. If another
    user has created it, the connection is closed with the closing code 1011.

    If the specified submission identifier does not exist, the connection is closed with
    the closing code 1011.

    Yoy may optionally specify a minimum entry number from which onwards to return log
    entries. Use the `from-entry-number` query parameter for this. For example, if you
    are only interested in status changes, you could choose a `from-entry-number` like
    100000.

    When you connect to this endpoint (and have sent a valid token), the current status
    and the existing log entries are sent. The endpoint checks the database every few
    seconds for new log entries or status changes, and it returns a JSON object with
    the current status (irrespective of whether it has changed or not) and the list of
    new log entries (or an empty list if there are no new entries). Here are two
    examples with two and no new log entries, respectively:

    .. code-block:: json
       {
           "status": "In progress",
           "log_entries: [
               {
                   "entry_number": 14,
                   "logged_at": "2022-05-03T08:16:56Z",
                   "message_type": "Info",
                   "message": "Mapping block NGC 6000..."
               },
               {
                   "entry_number": 15,
                   "logged_at": "2022-05-03T08:17:01Z",
                   "message_type": "Info",
                   "message": "Mapping block NGC 6001..."
               },
           ]
       }

    .. code-block:: json
       {
           "status": "In progress",
            "log_entries": []
       }

    If the submission is successful, a JSON object is sent which in addition includes
    the proposal code:

    .. code-block:: json
       {
           "status": "Successful",
           "log_entries": [
               {
                   "entry_number": 20,
                   "logged_at": "2022-05-03T08:17:34Z",
                   "message_type": "Info",
                   "message": "The submission was successful."
               }
           ],
           "proposal_code": "2022-1-SCI-042"
       }

    The entry_number of a log entry is a running number for a submission. In other
    words, the n-th log entry created for a submission has the entry number n.
    """
    include_from_entry_number = from_entry_number

    await websocket.accept()

    # Authenticate the user
    token = await websocket.receive_text()
    try:
        user: Optional[User] = find_user_from_token(token)
    except Exception:
        user = None
    if user is None:
        await websocket.send_text(
            "You are not authenticated. The first message sent "
            "to this endpoint must be a valid JWT token, which "
            "you should have obtained from the /token endpoint."
        )
        await websocket.close(1011)
        return

    with UnitOfWork() as unit_of_work:
        submission_repository = SubmissionRepository(unit_of_work.connection)

        # Check that the authenticated user made the submission (and, implicitly, that
        # the identifier exists).
        try:
            submission = submission_repository.get(identifier)
        except NotFoundError:
            await websocket.send_text(f"Unknown submission identifier: {identifier}")
            await websocket.close(1011)
            return
        if submission["submitter_id"] != user.id:
            await websocket.send_text(
                "You cannot access the submission log as someone else made the "
                "submission."
            )
            await websocket.close(1011)
            return

        while True:
            # Get the submission status and log entries
            submission_progress = submission_repository.get_progress(
                identifier=identifier,
                from_entry_number=include_from_entry_number,
            )

            # Next time we shouldn't include any log entries we got now.
            if len(submission_progress["log_entries"]) > 0:
                include_from_entry_number = 1 + max(
                    log_entry["entry_number"]
                    for log_entry in submission_progress["log_entries"]
                )

            # Send a message with the current status, new log entries and (in case of a
            # successful submission) proposal code.
            await websocket.send_json(submission_progress)

            if submission_progress["status"] != SubmissionStatus.IN_PROGRESS.value:
                await websocket.close()
                return

            await asyncio.sleep(TIME_BETWEEN_DB_QUERIES)


def _submission_details(
    identifier: str, from_entry_number: int, submission_repository: SubmissionRepository
) -> Dict[str, Any]:
    submission = submission_repository.get(identifier)
    log_entries = submission_repository.get_log_entries(identifier, from_entry_number)
    for log_entry in log_entries:
        log_entry["message_type"] = log_entry["message_type"].value
    return {
        "submitter_id": submission["submitter_id"],
        "status": submission["status"].value,
        "log_entries": log_entries,
    }
