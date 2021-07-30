from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.schemas import Phase2Proposal

app = FastAPI()
origins = [
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class P(BaseModel):
    pc: str

    class Config:
        orm_mode = True


@app.get("/{proposal_code}", response_model=Phase2Proposal)
def home(proposal_code: str) -> Any:
    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        return proposal_repository.get(proposal_code)

#  TODO the below method does exactly what home does fix response_model on home.
@app.get("/proposal/{proposal_code}")
def proposal(proposal_code: str) -> Any:
    with UnitOfWork() as unit_of_work:
        proposal_repository = ProposalRepository(unit_of_work.connection)
        return proposal_repository.get(proposal_code)
