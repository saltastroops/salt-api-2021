from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette import status

from saltapi.exceptions import NotFoundError
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.service.user import UserUpdate
from saltapi.service.user_service import UserService
from saltapi.web.schema.common import Message
from saltapi.web.schema.user import PasswordResetRequest, User

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "/send-password-reset-email",
    summary="Request an email with a password reset link to be sent.",
    response_description="Success message.",
    response_model=Message,
)
def send_password_reset_email(
    password_reset_request: PasswordResetRequest = Body(
        ..., title="Password reset request", description="Password reset request"
    ),
) -> Message:
    """
    Requests to send an email with a link for resetting the password. A username or
    email address needs to be supplied, and the email will be sent to the user with that
    username or email address.
    """
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Username or email didn't match any user.",
            )

        user_service = UserService(user_repository)
        user_service.send_password_reset_email(user)

        return Message(message="Email with a password reset link sent.")


@router.patch(
    "/{username}", summary="Update user details", response_model=User, status_code=200
)
def update_user_details(
    username: str = Query(
        ...,
        title="Username",
        description="Username of the user whose details are updated.",
    ),
    user: UserUpdate = Body(..., title="User Details", description="??"),
    auth_user: _User = Depends(get_current_user),
) -> _User:
    with UnitOfWork() as unit_of_work:

        # if auth_user.username != user.username or auth_user.email != user.email:
        #     raise HTTPException(
        #         status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        #         detail="Not allowed to update user.",
        #     )
        user_repository = UserRepository(unit_of_work.connection)
        user_service = UserService(user_repository)
        user_repository.connection.commet()
        return user_service.update_user_details(username, user)
