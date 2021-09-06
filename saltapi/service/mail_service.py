import smtplib

from saltapi.service.user import User
from saltapi.settings import Settings


class MailService:
    @staticmethod
    def send_password_reset_email(token: str, user: User):
        reset_url = MailService.password_reset_url(token)

        message = """From: SALT Team <{sender}>
    To: {user} <{receiver}>
    Subject: WEB Manager password reset

    Dear {user},

    Someone (probably you) has requested to reset your SALT Web Manager password.

    Please click on the link below to reset your password:

    {reset_url}

    Alternatively you can copy the link into the address bar of your browser.

    If you have not requested ton reset your password, you can just ignore this email.

    Kind regards,

    SALT Team
            """.format(
            sender=Settings().email,
            user="{given_name} {family_name}".format(
                family_name=user.family_name, given_name=user.given_name),
            receiver=user.email,
            reset_url=reset_url
        )

        try:
            smtp_obj = smtplib.SMTP(Settings().smtp_server)
            smtp_obj.sendmail(Settings().email, [user.email], message)
        except:
            raise ValueError("Failed to send reset password email.")

    @staticmethod
    def password_reset_url(token) -> str:
        return Settings().frontend_uri + "/reset-password/" + token