from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from saltapi.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from saltapi.logging_config import setup_logging
from saltapi.settings import get_settings
from saltapi.web.api.authentication import router as authentication_router
from saltapi.web.api.block_visits import router as block_visits_router
from saltapi.web.api.blocks import router as blocks_router
from saltapi.web.api.finder_charts import router as finder_charts_router
from saltapi.web.api.institutions import router as institution_router
from saltapi.web.api.instruments import router as instruments_router
from saltapi.web.api.proposal_progress import router as progress_router
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.api.submissions import router as submissions_router
from saltapi.web.api.user import router as user_router
from saltapi.web.api.users import router as users_router

app = FastAPI()


settings = get_settings()
origins = [settings.frontend_uri]

setup_logging(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> Response:
    return JSONResponse(status_code=404, content={"message": "Not Found"})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> Response:
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(
    request: Request, exc: AuthorizationError
) -> Response:
    return JSONResponse(status_code=403, content={"message": "Forbidden"})


app.include_router(progress_router)
app.include_router(blocks_router)
app.include_router(proposals_router)
app.include_router(authentication_router)
app.include_router(block_visits_router)
app.include_router(user_router)
app.include_router(users_router)
app.include_router(instruments_router)
app.include_router(institution_router)
app.include_router(submissions_router)
app.include_router(finder_charts_router)
