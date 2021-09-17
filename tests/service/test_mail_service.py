
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest

from saltapi.service.mail_service import MailService
from saltapi.service.user import User
from saltapi.settings import Settings

settings = Settings()

class MockSMTP:
    def __init__(self, *args, **kwargs):
        pass

    def sendmail(self, *args, **kwargs):
        if 'invalid@email.com' in kwargs['to_addrs']:
            raise Exception("Can not send to this address")


mail_service = MailService()
message = MIMEMultipart()
user = User(
            id=6,
            username='valid',
            given_name='valid',
            family_name='valid',
            email='valid@mail.com',
            password_hash='hashed_password'
        )


def test_send_generate_email_return_correct_message(monkeypatch):
    to = "Test User <test.user@email.com>"
    plain_body = "Test plain body"
    html_body = "<body>Test html body</body>"
    subject = "Test subject"
    message = mail_service.generate_email(
        to=to,
        plain_body=plain_body,
        html_body=html_body,
        subject=subject
    )
    
    assert message["To"] == to
    assert message["From"] == f"SALT Team <{settings.from_email}>"
    assert message["Subject"] == subject

