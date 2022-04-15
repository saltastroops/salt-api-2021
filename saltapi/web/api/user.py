from fastapi import APIRouter, Depends, Path

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.web import services
from saltapi.web.schema.user import User

router = APIRouter(tags=["User"])


@router.get(
    "/user",
    summary="Get your own user details",
    response_description="User details",
    response_model=User,
)
def who_am_i(user: _User = Depends(get_current_user)) -> _User:
    """
    Get the user details of the user making the request. These include contact details
    as well as user roles.
    """
    with UnitOfWork() as unit_of_work:
        user_service = services.user_service(unit_of_work.connection)
        user_details = user_service.get_user(user.username)

        return user_details


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
