
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List

from saltapi.service.user import User
from saltapi.settings import Settings


settings = Settings()


class MailService:
    @staticmethod
    def send_email(
            to: List[str],
            message: MIMEMultipart
    ) -> None:
        try:
            smtp_obj = smtplib.SMTP(settings.smtp_server)
            smtp_obj.sendmail(
                msg=message.as_string(),
                from_addr=settings.from_email,
                to_addrs=to

            )
        except Exception as e:
            raise Exception(f'Failed to send email: {e}')


    @staticmethod
    def generate_email(
            to: str,
            subject: str,
            html_body: str,
            plain_body: str,
    ) -> MIMEMultipart:
        """Generate a MIMEMultipart email"""
        message = MIMEMultipart('alternative')

        message['Subject'] = subject
        message['To'] = to
        message['From'] = f'SALT Team <{settings.from_email}>'
        message.attach(MIMEText(plain_body, 'plain'))
        message.attach(MIMEText(html_body, 'html'))
        return message

