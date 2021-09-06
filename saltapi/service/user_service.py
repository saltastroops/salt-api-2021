from datetime import timedelta

from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.mail_service import MailService
from saltapi.service.user import User, UserToUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, username: str) -> User:
        return self.repository.get(username)

    def email_token(self, user: User):
        authentication_service = AuthenticationService(self.repository)
        token_payload = {
            "username": user.username
        }
        reset_token = authentication_service.jwt_token(
            token_payload,
            timedelta(hours=24)
        )

        MailService.send_password_reset_email(reset_token, user)

    def update_user_details(self, user_to_update: UserToUpdate, user: User):
        self.repository.update_user_details(user_to_update, user)
