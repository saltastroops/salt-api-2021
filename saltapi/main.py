from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from saltapi.repository.authentication import AuthenticationRepository, \
    is_user_admin_or_salt_astronomer
from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authenticate import AccessToken
from saltapi.service.block_service import BlockService
from saltapi.web.api.proposals import router as proposals_router
from saltapi.web.schema.block import Block

app = FastAPI()
origins = [
    "http://127.0.0.1:4200",
]

app.include_router(proposals_router, prefix="/proposals")


@app.get("/{block_id}", response_model=Block)
def home(block_id: int, user=Depends(is_user_admin_or_salt_astronomer)) -> Any:
    with UnitOfWork() as unit_of_work:
        # proposals_dir = Settings().proposals_dir
        target_repository = TargetRepository(unit_of_work.connection)
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            target_repository, instrument_repository, unit_of_work.connection
        )
        block_service = BlockService(block_repository)
        return block_service.get_block(block_id)


@app.post('/token',
          summary="Request an authentication token",
          response_description="An authentication token",
          response_model=AccessToken)
def token(form_data: OAuth2PasswordRequestForm = Depends()) -> AccessToken:
    """
    Request an authentication token.

    The token returned can be used as an OAuth2 Bearer token for authenticating to the
    API. For example (assuming the token is `abcd1234`):

    ```shell
    curl -H "Authorization: Bearer abcd1234" /api/some/secret/resource
    ```
    The token is effectively a password; so keep it safe and don't share it.

    Note that the token expires 24 hours after being issued.
    """
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)
            authentication_repository = AuthenticationRepository(
                unit_of_work.connection,
                user_repository
            )
            user = authentication_repository.authenticate_user(form_data.username,
                                                               form_data.password)
            if user:
                return authentication_repository.access_token(user)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )


@app.get("/secret/{value}")
def secret(value: str, user=Depends(is_user_admin_or_salt_astronomer)):
    return {"new_value": user}


