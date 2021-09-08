from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import UserToUpdate
from saltapi.service.user_service import UserService


class ResponseMessage(BaseModel):
    message: str


router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "/send-password-reminder",
    summary="User request for password rest link",
    response_description="Success message.",
    response_model=ResponseMessage
)
def forgot_password(username: Optional[str]=None, email: Optional[str]=None) -> ResponseMessage:
    with UnitOfWork() as unit_of_work:
        user_repository = UserRepository(unit_of_work.connection)
        # check if either email or username is provided.
        if not username and not email:
            raise ValueError("Either username or email should be provided.")
        # verify username
        if username:
            user = user_repository.get(username)
        else:
            user = user_repository.get_by_email(email)

        if not user:
            raise ValueError("User not found.")
        user_service = UserService(user_repository)
        user_service.email_token(user)

        return ResponseMessage(
            message="Email with a password reset link sent."
        )


@router.post(
    "/update-user-details",
    summary="User password is reset.",
    response_description="Email has been send to the user with the password reset "
                         "token."
)
def password_reset(to_update_user: UserToUpdate, user=Depends(get_current_user)) -> Dict[str, str]:
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)

            user_service = UserService(user_repository)
            user_service.update_user_details(to_update_user, user)

            return {
                "message": "Password has been reset."
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )