
import smtplib
from email.mime.multipart import MIMEMultipart

import pytest

from saltapi.service.mail_service import MailService
from saltapi.service.user import User


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


def test_send_email_raises_an_error_for_invalid_email(monkeypatch):
    with pytest.raises(Exception) as e:
        monkeypatch.setattr(smtplib, 'SMTP', MockSMTP)
        user = User(
            id=6,
            username='invalid',
            given_name='invalid',
            family_name='invalid',
            email='invalid@email.com',
            password_hash='hashed_password'
        )
        MailService().send_email(
            to=[user.email],
            message=message,
        )


def test_send_email_raises_an_error_for_valid_email(monkeypatch):
    try:
        monkeypatch.setattr(smtplib, 'SMTP', MockSMTP)
        MailService().send_email(
            to=[user.email],
            message=message
        )
    except Exception as exc:
        assert False, 'Valid email raised and error.'
