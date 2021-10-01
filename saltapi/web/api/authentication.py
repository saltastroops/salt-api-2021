from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication import AccessToken
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.user import User

router = APIRouter(tags=["Authentication"])


def get_user_authentication_function() -> Callable[[str, str], User]:
    """
        Return the function for authenticating a user by username and password.
    ="""

    def authenticate_user(username: str, password: str) -> User:
        with UnitOfWork() as unit_of_work:
            user_repository = UserRepository(unit_of_work.connection)
            authentication_repository = AuthenticationService(user_repository)
            user = authentication_repository.authenticate_user(username, password)
            return user

    return authenticate_user


@router.post(
    "/token",
    summary="Request an authentication token",
    response_description="An authentication token",
    response_model=AccessToken,
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authenticate_user: Callable[[str, str], User] = Depends(
        get_user_authentication_function
    ),
) -> AccessToken:
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
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if user:
            return AuthenticationService.access_token(user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
