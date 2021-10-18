from datetime import timedelta
from typing import Any, Dict, List

from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.mail_service import MailService
from saltapi.service.user import Role, User
from saltapi.settings import Settings


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, username: str) -> User:
        return self.repository.get(username)

    def send_password_reset_email(self, user: User) -> None:
        mail_service = MailService()
        authentication_service = AuthenticationService(self.repository)
        reset_token = authentication_service.jwt_token(
            {"username": user.username}, timedelta(hours=24)
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
        return Settings().frontend_uri + "/reset-password/" + token

    def get_user_roles(self, username: str) -> List[Role]:
        return self.repository.get_user_roles(username)

    def get_user_details(self, username: str) -> Dict[str, Any]:
        contact_details = self.repository.get(username)
        roles = self.repository.get_user_roles(username)

        return {
            "username": username,
            "given_name": contact_details.given_name,
            "family_name": contact_details.family_name,
            "email": contact_details.email,
            "roles": roles,
        }
