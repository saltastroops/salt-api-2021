from typing import Dict

from fastapi import APIRouter, Depends

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.service.user_service import UserService
from saltapi.web.schema.user import User as UserDetails

router = APIRouter(tags=["User"])


@router.get(
    "/who-am-i",
    summary="Get your own user details",
    response_description="User details",
    response_model=UserDetails,
)
def who_am_i(user: User = Depends(get_current_user)) -> Dict[str, str]:
    """
    Get the user details of the user making the request. These include contact details
    as well as user roles.
    """
    with UnitOfWork() as unit_of_work:
        user_repository = UserRepository(unit_of_work.connection)
        user_service = UserService(user_repository)
        user_details = user_service.get_user_details(user.username)

        return user_details
