from datetime import datetime
from typing import Optional

import pytest
import pytz
from sqlalchemy.engine import Connection

# TODO: Add more tests
from saltapi.exceptions import NotFoundError, ValidationError
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.service.submission import SubmissionMessageType
from saltapi.service.user import User


def _dummy_user() -> User:
    return User(
        id=4,
        username="john",
        given_name="John",
        family_name="Doe",
        email="john@example.com",
        alternative_emails=[],
        password_hash="abc",
        affiliations=[],
        roles=[],
    )


def test_get_submission(dbconnection: Connection) -> None:
    """Test that submission details are returned."""
    submission_repository = SubmissionRepository(dbconnection)
    submission = submission_repository.get("a63e548d-ffa5-4213-ad8a-b44b1ec8a01c")
    assert submission["proposal_code"] is None
    assert submission["submitter_id"] == 1243
    assert submission["status"] == "In progress"
    assert submission["started_at"] == datetime(
        2022, 4, 25, 10, 7, 37, 0, tzinfo=pytz.utc
    )
    assert submission["finished_at"] == datetime(
        2022, 4, 25, 10, 10, 10, 0, tzinfo=pytz.utc
    )


def test_get_submission_fails_for_non_existing_identifier(
    dbconnection: Connection,
) -> None:
    """Test that an error is raised for a non-existing identifier."""
    submission_repository = SubmissionRepository(dbconnection)
    with pytest.raises(NotFoundError):
        submission_repository.get("idontexist")


def test_get_log_entries_for_existing_identifier(dbconnection: Connection) -> None:
    """Test that log entries are returned."""
    submission_repository = SubmissionRepository(dbconnection)
    log_entries = submission_repository.get_log_entries(
        "a63e548d-ffa5-4213-ad8a-b44b1ec8a01c"
    )

    assert len(log_entries) == 1
    assert log_entries[0]["entry_number"] == 1
    assert log_entries[0]["message_type"] == "Info"
    assert log_entries[0]["message"] == "Starting submission."
    assert log_entries[0]["logged_at"] == datetime(
        2022, 4, 25, 12, 7, 38, 0, tzinfo=pytz.utc
    )


def test_get_log_entries_for_non_existing_identifier(dbconnection: Connection) -> None:
    """Test that an empty list is returned for a non-existing identifier."""
    submission_repository = SubmissionRepository(dbconnection)
    log_entries = submission_repository.get_log_entries("idontexist")

    assert len(log_entries) == 0


def test_get_log_entries_from_entry_number(dbconnection:Connection) -> None:
    """Test that the returned log entries can be limited."""
    submission_repository = SubmissionRepository(dbconnection)
    user = _dummy_user()
    identifier = submission_repository.create_submission(user=user, proposal_code=None)

    submission_repository.create_log_entry(identifier, SubmissionMessageType.INFO, "Message 1")
    submission_repository.create_log_entry(identifier, SubmissionMessageType.ERROR, "Message 2")
    submission_repository.create_log_entry(identifier, SubmissionMessageType.WARNING, "Message 3")

    log_entries = submission_repository.get_log_entries(identifier, from_entry_number=2)

    assert len(log_entries) == 2
    assert log_entries[0]["entry_number"] == 2
    assert log_entries[1]["entry_number"] == 3



@pytest.mark.parametrize("proposal_code", [None, "2021-2-SCI-004"])
def test_create_submission(proposal_code: Optional[str], dbconnection: Connection) -> None:
    """Test that a submission is created."""
    submission_repository = SubmissionRepository(dbconnection)
    user = _dummy_user()
    identifier = submission_repository.create_submission(user=user, proposal_code=proposal_code)
    submission = submission_repository.get(identifier)
    assert submission["submitter_id"] == user.id
    assert submission["proposal_code"] == proposal_code


def test_create_submission_fails_for_unknown_proposal_code(dbconnection: Connection):
    """Test that a submission cannot be created for a non-existing proposal code."""
    submission_repository = SubmissionRepository(dbconnection)
    user = _dummy_user()
    with pytest.raises(ValidationError) as excinfo:
        submission_repository.create_submission(user=user, proposal_code="idontexist")
    assert "idontexist" in str(excinfo.value)


def test_create_log_entry(dbconnection: Connection) -> None:
    """Test creating a log entry."""
    submission_repository = SubmissionRepository(dbconnection)
    user = _dummy_user()
    identifier = submission_repository.create_submission(user=user, proposal_code=None)

    submission_repository.create_log_entry(identifier, SubmissionMessageType.INFO, "Checking exposure times.")
    submission_repository.create_log_entry(identifier, SubmissionMessageType.ERROR, "An exposure time cannot be negative.")

    log_entries = submission_repository.get_log_entries(identifier)

    assert len(log_entries) == 2

    assert log_entries[0]["entry_number"] == 1
    assert log_entries[0]["message_type"] == "Info"
    assert log_entries[0]["message"] == "Checking exposure times."

    assert log_entries[1]["entry_number"] == 2
    assert log_entries[1]["message_type"] == "Error"
    assert log_entries[1]["message"] == "An exposure time cannot be negative."
