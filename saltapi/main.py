from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from saltapi.web.api.proposals import router as proposals_router

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")


class P(BaseModel):
    pc: str

    class Config:
        orm_mode = True


@app.get("/")
def home() -> Any:
    # with UnitOfWork() as unit_of_work:
    # user_repository = UserRepository(unit_of_work.connection)
    # user_service = UserService(user_repository)
    # user = user_service.get_user("")
    return {"success": True}
    # proposal_repository = ProposalRepository(unit_of_work.connection)
    # proposal_service = ProposalService(proposal_repository)
    # v = proposal_service.list_proposal_summaries()
    # return [ProposalListItem.from_orm(p) for p in v]
