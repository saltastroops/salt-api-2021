from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from saltapi.settings import Settings
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.api.authentication import router as authentication_router

app = FastAPI()
origins = [
    Settings().frontend_uri
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proposals_router, prefix="/proposals")
app.include_router(authentication_router, prefix="/authentication")

