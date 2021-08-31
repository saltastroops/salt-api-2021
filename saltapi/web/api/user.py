from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user_service import UserService

router = APIRouter(tags=["User"])


@router.post(
    "/forgot-password",
    summary="User request for password rest link",
    response_description="Email has been send to the user with the password reset "
                         "token."
)
def forgot_password(username: str) -> Dict[str, str]:
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)
            # verify username
            user = user_repository.get(username)
            if not user:
                raise ValueError("User not found.")
            user_service = UserService(user_repository)
            user_service.email_token(user)

            return {
                "message": "Reset password token was sent successfully."
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.post(
    "/password-reset",
    summary="User password is reset.",
    response_description="Email has been send to the user with the password reset "
                         "token."
)
def password_reset(username: str) -> Dict[str, str]:
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)
            # verify username
            user = user_repository.get(username)
            if not user:
                raise ValueError("User not found.")
            user_service = UserService(user_repository)
            user_service.email_token(user)

            return {
                "message": "Reset password token was sent successfully."
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )