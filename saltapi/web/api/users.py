from fastapi import APIRouter, Body, HTTPException
from starlette import status

from saltapi.exceptions import NotFoundError
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
    password_reset_request: PasswordResetRequest = Body(
        ..., title="Password reset request", description="Password reset request"
    ),
) -> Message:

    with UnitOfWork() as unit_of_work:
        username_email = password_reset_request.username_email
        user_repository = UserRepository(unit_of_work.connection)
        try:
            try:
                user = user_repository.get(username_email)
            except NotFoundError:
                user = user_repository.get_by_email(username_email)

        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username or email didn't match any user.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_service = UserService(user_repository)
        user_service.send_password_reset_email(user)

        return Message(
            message="Email with a password reset link sent."
        )
