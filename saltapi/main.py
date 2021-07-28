from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.schemas import Phase2Proposal

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")


class P(BaseModel):
    pc: str

    class Config:
        orm_mode = True


@app.get("/{proposal_code}", response_model=Phase2Proposal)
def home(proposal_code: str) -> Any:
    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        return proposal_repository.get(proposal_code)
