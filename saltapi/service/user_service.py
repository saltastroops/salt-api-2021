import smtplib
from datetime import timedelta

from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.user import User
from saltapi.settings import Settings


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
        self.send_reset_token_email(reset_token, user)

    def reset_password(self, password: str, token: str):
        # Get username from token
        # update the password
        # Email a successful update of pass word
        pass

    @staticmethod
    def send_reset_token_email(token: str, user: User):
        reset_token = Settings().frontend_uri + "/reset-password/" + token

        message = """From: SALT Team <{sender}>
To: {user} <{receiver}>
Subject: WEB Manager password reset

Please click on the link below to reset your password:
{reset_token}

Regards
SALT Team
        """.format(
            sender=Settings().email,
            user="{family_name} {given_name}".format(
                family_name=user.family_name, given_name=user.given_name),
            receiver=user.email,
            reset_token=reset_token
        )

        try:
            smtpObj = smtplib.SMTP('localhost')  # TODO need to use SAAO SMTP
            smtpObj.sendmail(Settings().email, [user.email], message)
        except smtplib.SMTPException:
            raise ValueError("Failed to send reset password email.")
