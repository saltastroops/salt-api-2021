from typing import List, Dict, Any

from fastapi import (
    APIRouter,
)

from saltapi.repository.user_repository import UserRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.user_service import UserService


router = APIRouter(prefix="/salt-astronomers", tags=["SALT-Astronomers"])


@router.get("/", summary="List of SALT astronomers", response_model=List[Dict[str, Any]])
def get_list_of_astronomers() -> List[Dict[str, Any]]:
    """
    List of SALT astronomers.
    """

    with UnitOfWork() as unit_of_work:
        user_repository = UserRepository(unit_of_work.connection)
        user_service = UserService(user_repository)
        return user_service.list_salt_astronomers()
