from typing import Optional

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import User


class FakeUserRepository(UserRepository):
    def get(self, username: str) -> Optional[User]:
        if username == "jdoe":
            return User(
                id=1,
                username='jdoe',
                given_name="John",
                family_name="Doe",
                email="johndoe@email.com",
                password_hash="hasdedpassword"
            )
        return None

    def find_user_with_username_and_password(self,username, password):
        if username == "jdoe" and password == "hasdedpassword":
            return User(
                id=1,
                username='jdoe',
                given_name="John",
                family_name="Doe",
                email="johndoe@email.com",
                password_hash="hasdedpassword"
            )

        raise NotFoundError("User not found or password doesn't match.")
