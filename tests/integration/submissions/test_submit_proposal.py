import time
import zipfile
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy.engine import Connection
from starlette import status

import saltapi.service.submission_service
from saltapi.repository.submission_repository import SubmissionRepository
from tests.conftest import authenticate, find_username


def test_submission_requires_authentication(client: TestClient, tmp_path: Path) -> None:
    proposal = tmp_path / "proposal.zip"
    with zipfile.ZipFile(proposal, "w") as z:
        content = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns1:Proposal code="2021-2-SCI-042" xmlns:ns1="https://example.com">
</ns1:Proposal>
        """
        with z.open("Proposal.xml", "w") as f:
            f.write(content)
    files = {"proposal": open(proposal, "rb")}
    response = client.post(
        "/submissions/", params={"proposal-code": "2022-1-SCI-243"}, files=files
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_submission_requires_a_file(client: TestClient) -> None:
    """Test that a proposal submission must include a file."""
    username = find_username("administrator")
    authenticate(username, client)
    response = client.post("/submissions/")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_submission_file_must_be_zipfile(client: TestClient, tmp_path: Path) -> None:
    """Test that the submitted file must be a zipfile."""
    username = find_username("administrator")
    authenticate(username, client)
    proposal = tmp_path / "proposal.txt"
    proposal.write_bytes(b"This is not a zipfile.")
    files = {"proposal": open(proposal, "rb")}
    response = client.post("/submissions/", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "be a zip" in response.json()["message"]


def test_submission_file_must_contain_xml(client: TestClient, tmp_path: Path) -> None:
    """Test that the submitted file must contain a Proposal.xml file."""
    username = find_username("administrator")
    authenticate(username, client)
    proposal = tmp_path / "proposal.zip"
    with zipfile.ZipFile(proposal, "w") as z:
        with z.open("Something.xml", "w") as f:
            f.write(b"Some content")
    files = {"proposal": open(proposal, "rb")}
    response = client.post("/submissions/", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    message = response.json()["message"]
    assert "Proposal.xml" in message and "Blocks.xml" in message


def test_proposal_code_must_be_consistent(client: TestClient, tmp_path: Path) -> None:
    """Test that proposal codes in a query parameter and in the XML must be the same."""
    username = find_username("administrator")
    authenticate(username, client)
    proposal = tmp_path / "proposal.zip"
    with zipfile.ZipFile(proposal, "w") as z:
        content = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns1:Proposal code="2021-2-SCI-042" xmlns:ns1="https://example.com">
</ns1:Proposal>
        """
        with z.open("Proposal.xml", "w") as f:
            f.write(content)
    files = {"proposal": open(proposal, "rb")}
    response = client.post(
        "/submissions/", params={"proposal-code": "2022-1-SCI-243"}, files=files
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    message = response.json()["message"]
    assert "2022-1-SCI-243" in message and "2021-2-SCI-042" in message


@pytest.mark.parametrize("successful", [True, False])
def test_submission(
    successful: bool,
    client: TestClient,
    dbconnection: Connection,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """
    Test that submitting a proposal us working.

    This test mocks the call to the external submission tool, and this mock call does
    not mark the submission as finished in the database. This implies that the test
    does not cover the case that the submission tool properly marks the submission as
    finished. Testing this case wouyld be hard: We would have to test that code running
    in a separate thread does *not* do something, which would mean we have to wait for
    a while to ensure nothing has happened. As this would considerably slow down the
    test execution, we ignore this case.
    """
    username = find_username("administrator")
    authenticate(username, client)
    proposal = tmp_path / "proposal.zip"
    with zipfile.ZipFile(proposal, "w") as z:
        content = b"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns1:Proposal code="2021-2-SCI-042" xmlns:ns1="https://example.com">
</ns1:Proposal>
            """
        with z.open("Proposal.xml", "w") as f:
            f.write(content)
    files = {"proposal": open(proposal, "rb")}

    def mock_call_submission_tool(*args: Any, **kwargs: Any) -> int:
        return 0 if successful else -1

    monkeypatch.setattr(
        saltapi.service.submission_service.SubmissionService,
        "_call_submission_tool",
        mock_call_submission_tool,
    )

    response = client.post("/submissions/", files=files)

    assert response.status_code == status.HTTP_202_ACCEPTED

    identifier = response.json()["submission_identifier"]

    # As our mock submission call does not mark the submission as finished, the
    # submission service should. But this is happening in a separate thread and hence
    # at this point may not have been accomplished yet. Hence we have to wait for it
    # to happen. We check several times, with increasing wait times between the tries.
    wait_times = [0, 0.01, 0.05, 0.1, 0.5, 1, 3]
    passed = False
    submission_repository = SubmissionRepository(dbconnection)
    for t in wait_times:
        time.sleep(t)
        submission = submission_repository.get(identifier)
        log_entries = submission_repository.get_log_entries(identifier)
        if successful:
            if len(log_entries) == 0 or "unclear" not in log_entries[-1]["message"]:
                continue
        else:
            if len(log_entries) == 0 or "failed" not in log_entries[-1]["message"]:
                continue
        if submission["finished_at"] is None:
            continue

        passed = True
        break

    assert passed, "The submission has not been marked as finished in the database."
