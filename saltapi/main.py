from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from saltapi.logging_config import setup_logging
from saltapi.settings import Settings
from saltapi.web.api.authentication import router as authentication_router
from saltapi.web.api.blocks import router as blocks_router
from saltapi.web.api.proposals import router as proposals_router

app = FastAPI()

setup_logging(app)

settings = Settings()
origins = [settings.frontend_uri]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blocks_router)
app.include_router(proposals_router)
app.include_router(authentication_router)
