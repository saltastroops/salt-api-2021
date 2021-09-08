import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from saltapi.service.user import User
from saltapi.settings import Settings


class EmailMessagePart:
    plain:  MIMEText
    html:  MIMEText


class MailService:
    @staticmethod
    def send_email(
            emails_to: List[str],
            email_from: str,
            email_message: MIMEMultipart,
    ):

        try:
            smtp_obj = smtplib.SMTP(Settings().smtp_server)
            smtp_obj.sendmail(email_from, emails_to, email_message.as_string())
        except:
            raise ValueError("Failed to send reset password from_email.")


