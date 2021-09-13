
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import List

from saltapi.service.user import User
from saltapi.settings import Settings


settings = Settings()


class MailService:
    @staticmethod
    def send_email(
            to: List[User],
            subject,
            html_body: str,
            plain_body: str
    ) -> None:

        try:
            to_txt = ",".join(
                f'{u.given_name} {u.family_name} <{u.email}>'
                for u in to
            )
            to = [u.email for u in to]

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['To'] = to_txt
            message['From'] = settings.from_email,
            message.attach(MIMEText(plain_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            smtp_obj = SMTP(settings.smtp_server)
            smtp_obj.sendmail(
                settings.from_email,
                to,
                message.as_string()
            )
        except Exception as e:
            raise ValueError(f"Failed to send email: {e}")
