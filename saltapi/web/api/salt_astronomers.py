from typing import List, Dict, Any

from fastapi import (
    APIRouter,
)

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.proposal_service import ProposalService


router = APIRouter(prefix="/salt-astronomers", tags=["SALT-Astronomers"])


@router.get("/", summary="List of SALT astronomers", response_model=List[Dict[str, Any]])
def get_list_of_astronomers() -> List[Dict[str, Any]]:
    """
    List of SALT astronomers.
    """

    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        proposal_service = ProposalService(proposal_repository)
        return proposal_service.list_salt_astronomers()
