from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.proposal_service import ProposalService
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.schemas import ProposalListItem

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")


class P(BaseModel):
    pc: str

    class Config:
        orm_mode = True


@app.get("/", response_model=List[ProposalListItem])
def home() -> List[ProposalListItem]:
    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        proposal_service = ProposalService(proposal_repository)
        v = proposal_service.list_proposal_summaries()
        return [ProposalListItem.from_orm(p) for p in v]
