from datetime import timedelta
from typing import Any, Dict, List

from saltapi.exceptions import NotFoundError, ValidationError
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.mail_service import MailService
from saltapi.service.user import NewUserDetails, Role, User, UserUpdate
from saltapi.settings import Settings


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def send_password_reset_email(self, user: User) -> None:
        mail_service = MailService()
        authentication_service = AuthenticationService(self.repository)
        reset_token = authentication_service.jwt_token(
            {"sub": str(user.id)}, timedelta(hours=1)
        )
        user_full_name = f"{user.given_name} {user.family_name}"

        password_reset_url = self.password_reset_url(reset_token)
        plain_body = f"""Dear {user_full_name},

Someone (probably you) has requested to reset your SALT Web Manager password.

Please click on the link below to reset your password:

{password_reset_url}

Alternatively you can copy the link into the address bar of your browser.

If you have not requested to reset your password, you can just ignore this email.

Kind regards,

SALT Team
        """

        html_body = f"""
<html>
  <head></head>
  <body>
    <p>Dear {user_full_name},</p>
    <p>Someone (probably you) has requested to reset your SALT Web Manager password.</p>
    <p>Please click on the link below to reset your password:</p>
    <p><a href="{password_reset_url}">{password_reset_url}</a>.</p>
    <p>Alternatively you can copy the link into the address bar of your browser.</p>
    <p>If you have not requested to reset your password, you can just ignore this
    email.</p>
    <p>Kind regards,</p>
    <p>SALT Team</p>
  </body>
</html>
        """
        message = mail_service.generate_email(
            to=f"{user.given_name} {user.family_name} <{user.email}>",
            html_body=html_body,
            plain_body=plain_body,
            subject="SALT Web Manager password reset",
        )
        mail_service.send_email(to=[user.email], message=message)

    @staticmethod
    def password_reset_url(token: str) -> str:
        return Settings().frontend_uri + "/change-password/" + token

    def get_user_roles(self, username: str) -> List[Role]:
        return self.repository.get_user_roles(username)

    def _does_user_exist(self, username: str) -> bool:
        try:
            self.get_user(username)
        except NotFoundError:
            return False

        return True

    def create_user(self, user: NewUserDetails) -> None:
        if self._does_user_exist(user.username):
            raise ValidationError(f"The username {user.username} exists already.")
        self.repository.create(user)

    def get_user(self, username: str) -> User:
        user = self.repository.get(username)
        user.password_hash = "***"  # Just in case the password hash ends up somewhere
        return user

    def get_users(self) -> List[Dict[str, Any]]:
        users_details = self.repository.get_users()
        return users_details

    def get_user_by_email(self, email: str) -> User:
        user = self.repository.get_by_email(email)
        user.password_hash = "***"  # Just in case the password hash ends up somewhere
        return user

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        user.password_hash = "***"  # Just in case the password hash ends up somewhere
        return user

    def update_user(self, username: str, user: UserUpdate) -> None:
        if user.username and self._does_user_exist(user.username):
            raise ValidationError(f"The username {user.username} exists already.")
        self.repository.update(username, user)
