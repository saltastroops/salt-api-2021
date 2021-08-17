import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('.')))


from typing import Any

from fastapi import FastAPI

from saltapi.logging_config import setup_logging
from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block_service import BlockService
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.schema.block import Block

app = FastAPI()

setup_logging()

app.include_router(proposals_router, prefix="/proposals")

@app.get("/{block_id}", response_model=Block)
def home(block_id: int) -> Any:
    with UnitOfWork() as unit_of_work:
        # proposals_dir = Settings().proposals_dir
        target_repository = TargetRepository(unit_of_work.connection)
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            target_repository, instrument_repository, unit_of_work.connection
        )
        block_service = BlockService(block_repository)
        return block_service.get_block(block_id)
