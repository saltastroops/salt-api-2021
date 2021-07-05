from fastapi import FastAPI

from saltapi.web.api.proposals import router as proposals_router

app = FastAPI()

app.include_router(proposals_router, prefix="/proposals")
