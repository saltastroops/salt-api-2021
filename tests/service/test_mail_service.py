
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

import pytest

from saltapi.service.mail_service import MailService
from saltapi.service.user import User


def test_send_email_raises_an_error_for_invalid_email(monkeypatch):
    def mock_send_email(*args, **kwargs):
        raise ValueError

    with pytest.raises(ValueError) as e:
        monkeypatch.setattr(MailService, "send_email", mock_send_email)
        user = User(
            id=6,
            username='invalid',
            given_name='invalid',
            family_name='invalid',
            email='invalid@mail.com',
            password_hash='hashed_password'
        )
        MailService().send_email(
            to=[user],
            subject="Email Subject",
            plain_body="",
            html_body="",
        )


def test_send_email_raises_an_error_for_valid_email(monkeypatch):
    def mock_send_email(*args, **kwargs):
        pass

    try:
        monkeypatch.setattr(MailService, "send_email", mock_send_email, raising=True)
        user = User(
            id=6,
            username='valid',
            given_name='valid',
            family_name='valid',
            email='valid@mail.com',
            password_hash='hashed_password'
        )
        MailService().send_email(
            to=[user],
            subject="Email Subject",
            plain_body="",
            html_body="",
        )
    except ZeroDivisionError as exc:
        assert False, 'Valid email raised and error.'
