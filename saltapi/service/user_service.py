from typing import List

from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import Role, User


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, username: str) -> User:
        return self.repository.get(username)

    def get_user_roles(self, username: str) -> List[Role]:
        return self.repository.get_user_roles(username)
