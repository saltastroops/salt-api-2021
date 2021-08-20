from typing import List

from fastapi import (
    APIRouter,
)

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.proposal_service import ProposalService
from saltapi.web.schema.proposal import ContactDetails

router = APIRouter(prefix="/salt-astronomers", tags=["SALT-Astronomers"])


@router.get("/", summary="List of SALT astronomers", response_model=List[ContactDetails])
def get_proposals() -> List[ContactDetails]:
    """
    Lists all proposals the user may view. The proposals returned can be limited to those
    with submissions within a semester range by supplying a from or a to semester (or
    both).
    """

    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        proposal_service = ProposalService(proposal_repository)
        return proposal_service.list_salt_astronomers()

