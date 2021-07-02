from fastapi import FastAPI

from saltapi.proposals.api import router as proposals_router

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")
