from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette import status

from saltapi.exceptions import NotFoundError
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import NewUserDetails as _NewUserDetails
from saltapi.service.user import User as _User
from saltapi.service.user import UserUpdate as _UserUpdate
from saltapi.web import services
from saltapi.web.schema.common import Message
from saltapi.web.schema.user import (
    NewUserDetails,
    PasswordResetRequest,
    User,
    UserListItem,
    UserUpdate,
)

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
        user_service = services.user_service(unit_of_work.connection)
        try:
            try:
                user = user_service.get_user(username_email)
            except NotFoundError:
                user = user_service.get_user_by_email(username_email)

        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Username or email didn't match any user.",
            )

        user_service.send_password_reset_email(user)

        return Message(message="Email with a password reset link sent.")


@router.post(
    "/",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
def create_user(
    user: NewUserDetails = Body(
        ..., title="User details", description="User details for the user to create."
    )
) -> _User:
    with UnitOfWork() as unit_of_work:
        user_service = services.user_service(unit_of_work.connection)
        user_service.create_user(
            _NewUserDetails(
                username=user.username,
                password=user.password,
                email=user.email,
                given_name=user.given_name,
                family_name=user.family_name,
                institute_id=user.institute_id,
            )
        )
        unit_of_work.commit()

        return user_service.get_user(user.username)


@router.get("/", summary="Get users information", response_model=List[UserListItem])
def get_users(
    user: _User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with UnitOfWork() as unit_of_work:
        user_service = services.user_service(unit_of_work.connection)
        return user_service.get_users()


@router.get("/{user_id}", summary="Get user details", response_model=User)
def get_user_by_id(
    user_id: int = Path(
        ...,
        alias="user_id",
        title="User id",
        description="User id of the user making the request.",
    ),
    user: _User = Depends(get_current_user),
) -> _User:
    with UnitOfWork() as unit_of_work:
        user_service = services.user_service(unit_of_work.connection)
        return user_service.get_user_by_id(user_id)


@router.get("/{username}", summary="Get user details", response_model=User)
def get_user(
    username: str = Path(
        ...,
        title="Username",
        description="Username of the user whose details are updated.",
    ),
    user: _User = Depends(get_current_user),
) -> _User:
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_user(user, username)
        user_service = services.user_service(unit_of_work.connection)
        return user_service.get_user(username)


@router.patch("/{username}", summary="Update user details", response_model=User)
def update_user(
    username: str = Path(
        ...,
        title="Username",
        description="Username of the user whose details are updated.",
    ),
    user_update: UserUpdate = Body(..., title="User Details", description="??"),
    user: _User = Depends(get_current_user),
) -> _User:
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_user(user, username)

        _user_update = _UserUpdate(
            username=user_update.username, password=user_update.password
        )
        user_service = services.user_service(unit_of_work.connection)
        user_service.update_user(username, _user_update)
        unit_of_work.commit()

        new_username = user_update.username if user_update.username else username
        return user_service.get_user(new_username)
