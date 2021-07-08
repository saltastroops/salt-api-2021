from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import User


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: int) -> User:
        return self.repository.get(user_id)
