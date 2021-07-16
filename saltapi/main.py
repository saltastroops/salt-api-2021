from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block_service import BlockService
from saltapi.settings import Settings
from saltapi.web.api.proposals import router as proposals_router

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")


class P(BaseModel):
    pc: str

    class Config:
        orm_mode = True


@app.get("/{block_id}")
def home(block_id: int) -> Any:
    with UnitOfWork() as unit_of_work:
        proposals_dir = Settings().proposals_dir
        block_reopository = BlockRepository(unit_of_work.connection, proposals_dir)
        block_service = BlockService(block_reopository)
        return block_service.get_block(block_id)
