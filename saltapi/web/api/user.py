from fastapi import APIRouter, Depends

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User as _User
from saltapi.service.user_service import UserService
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
        user_repository = UserRepository(unit_of_work.connection)
        user_service = UserService(user_repository)
        user_details = user_service.get_user(user.username)

        return user_details
