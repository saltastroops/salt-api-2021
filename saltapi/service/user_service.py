from datetime import timedelta

from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.mail_service import MailService
from saltapi.service.user import User, UserToUpdate
from saltapi.settings import Settings


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, username: str) -> User:
        return self.repository.get(username)

    def email_token(self, user: User):
        authentication_service = AuthenticationService(self.repository)
        reset_token = authentication_service.jwt_token(
            {"username": user.username},
            timedelta(hours=24)
        )
        user_txt = "{given_name} {family_name}".format(
                family_name=user.family_name, given_name=user.given_name)
        email_to = user.email
        email_from = Settings().from_email
        email_to_txt = '{user} <{receiver}>'.format(
            user=user_txt[0], receiver=user.email
        )
        email_from_txt = 'SALT Team <{sender}>'.format(sender=Settings().from_email)
        email_subject = 'WEB Manager password reset'

        plain_body = '''Dear {user},

Someone (probably you) has requested to reset your SALT Web Manager password.

Please click on the link below to reset your password:
{reset_url}.

Alternatively you can copy the link into the address bar of your browser.

If you have not requested to reset your password, you can just ignore this email.

Kind regards,

SALT Team
        '''.format(user=user_txt[0], reset_url=self.password_reset_url(reset_token))

        html_body = '''
<html>
  <head></head>
  <body>
    <p>Dear {user},</p>
    <p>Someone (probably you) has requested to reset your SALT Web Manager password.</p>
    <p>Please click on the link below to reset your password:</p>
    <p><a href="{reset_url}">password reset link</a>.</p>
    <p>Alternatively you can copy the link into the address bar of your browser.</p>
    <p>If you have not requested to reset your password, you can just ignore this email.</p>
    <p>Kind regards,</p>
    <p>SALT Team</p>
  </body>
</html>
        '''.format(user=user_txt[0], reset_url=self.password_reset_url(reset_token))

        message = MailService.generate_email(
            email_to=email_to_txt,
            email_from=email_from_txt,
            email_subject=email_subject,
            email_html_body=html_body,
            email_plain_body=plain_body,
        )

        MailService.send_email([email_to], email_from, message)

    def update_user_details(self, user_to_update: UserToUpdate, user: User):
        self.repository.update_user_details(user_to_update, user)

    @staticmethod
    def password_reset_url(token) -> str:
        return Settings().frontend_uri + "/reset-password/" + token
