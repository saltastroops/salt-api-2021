from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import User


class FakeUserRepository(UserRepository):
    def get(self, username: str):
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
