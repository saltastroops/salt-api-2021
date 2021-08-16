from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block_service import BlockService
from saltapi.web.api.blocks import router as blocks_router
from saltapi.web.api.proposals import router as proposals_router

app = FastAPI()
origins = ["http://127.0.0.1:4200", "http://localhost:4200"]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"]
)

app.include_router(blocks_router)
app.include_router(proposals_router)