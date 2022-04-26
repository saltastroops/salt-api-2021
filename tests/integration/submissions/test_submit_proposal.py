from pathlib import Path
import zipfile

from fastapi.testclient import TestClient
from starlette import status

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
