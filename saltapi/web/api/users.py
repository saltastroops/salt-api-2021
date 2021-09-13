from typing import Optional

from fastapi import APIRouter

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user_service import UserService
from saltapi.web.schema.common import Message

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "/send-password-reset-email",
    summary="Request an email with a password reset link to be sent.",
    response_description="Success message.",
    response_model=Message
)
def send_password_reset_email(
        username: Optional[str] = None,
        email: Optional[str] = None
) -> Message:
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
        user_service.send_password_reset_email(user)

        return Message(
            message="Email with a password reset link sent."
        )
