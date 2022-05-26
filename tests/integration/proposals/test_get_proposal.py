import pathlib
from typing import Any, NamedTuple

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from starlette import status

from tests.conftest import authenticate, find_username, not_authenticated

PROPOSALS_URL = "/proposals"


@pytest.mark.parametrize(
    "proposal_code",
    [
        "2018-2-LSP-001",
        "2016-1-COM-001",
        "2016-1-SVP-001",
        "2019-1-GWE-005",
        "2020-2-DDT-005",
    ],
)
def test_should_return_401_when_requesting_proposal_for_unauthorized_user(
    proposal_code: str,
    client: TestClient,
) -> None:
    not_authenticated(client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/" + proposal_code + extension,
            params={"proposal_code": proposal_code},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_non_existing_proposal(
    client: TestClient,
) -> None:
    username = find_username("administrator")
    proposal_code = "2020-2-SCI-099"
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/" + proposal_code + extension,
            params={"proposal_code": proposal_code},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2018-2-LSP-001"),
        find_username("Principal Contact", proposal_code="2018-2-LSP-001"),
        find_username("Principal Investigator", proposal_code="2018-2-LSP-001"),
        find_username("Administrator"),
        find_username("SALT Astronomer"),
        find_username("TAC Member", partner_code="RSA"),
        find_username("TAC Chair", partner_code="RSA"),
    ],
)
def test_should_return_proposal_when_requesting_science_proposal_for_permitted_users(
    username: str, client: TestClient
) -> None:
    proposal_code = "2018-2-LSP-001"

    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == proposal_code


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2018-2-LSP-001"),
        find_username("Principal Contact", proposal_code="2018-2-LSP-001"),
        find_username("Principal Investigator", proposal_code="2018-2-LSP-001"),
        find_username("TAC Member", partner_code="UW"),
        find_username("TAC Chair", partner_code="UW"),
        find_username("Board Member"),
    ],
)
def test_should_return_403_when_requesting_science_proposal_for_non_permitted_users(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/2019-2-SCI-006" + extension,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2020-2-DDT-005"),
        find_username("Principal Contact", proposal_code="2020-2-DDT-005"),
        find_username("Principal Investigator", proposal_code="2020-2-DDT-005"),
        find_username("Administrator"),
        find_username("SALT Astronomer"),
    ],
)
def test_should_return_proposal_when_requesting_ddt_proposal_for_permitted_users(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2020-2-DDT-005",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == "2020-2-DDT-005"


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2020-2-SCI-018"),
        find_username("Principal Contact", proposal_code="2020-2-SCI-018"),
        find_username("Principal Investigator", proposal_code="2020-2-SCI-018"),
        find_username("TAC Member", partner_code="RSA"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("TAC Member", partner_code="POL"),
        find_username("TAC Chair", partner_code="POL"),
        find_username("Board Member"),
    ],
)
def test_should_return_403_when_requesting_ddt_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/2020-2-DDT-005" + extension,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2016-1-COM-001"),
        find_username("Principal Contact", proposal_code="2016-1-COM-001"),
        find_username("Principal Investigator", proposal_code="2016-1-COM-001"),
        find_username("Administrator"),
        find_username("SALT Astronomer"),
    ],
)
def test_should_return_proposal_when_requesting_com_proposal_for_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2016-1-COM-001",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == "2016-1-COM-001"


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2018-2-LSP-001"),
        find_username("Principal Contact", proposal_code="2018-2-LSP-001"),
        find_username("Principal Investigator", proposal_code="2018-2-LSP-001"),
        find_username("TAC Member", partner_code="RSA"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("TAC Member", partner_code="POL"),
        find_username("TAC Chair", partner_code="POL"),
        find_username("Board Member"),
    ],
)
def test_should_return_403_when_requesting_com_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/2016-1-COM-001" + extension,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2016-1-SVP-001"),
        find_username("Principal Contact", proposal_code="2016-1-SVP-001"),
        find_username("Principal Investigator", proposal_code="2016-1-SVP-001"),
        find_username("Administrator"),
        find_username("SALT Astronomer"),
    ],
)
def test_should_return_proposal_when_requesting_sv_proposal_for_permitted_users(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2016-1-SVP-001",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == "2016-1-SVP-001"


@pytest.mark.parametrize(
    "username",
    [
        find_username("Investigator", proposal_code="2018-2-LSP-001"),
        find_username("Principal Contact", proposal_code="2018-2-LSP-001"),
        find_username("Principal Investigator", proposal_code="2018-2-LSP-001"),
        find_username("TAC Member", partner_code="RSA"),
        find_username("TAC Chair", partner_code="RSA"),
        find_username("TAC Member", partner_code="POL"),
        find_username("TAC Chair", partner_code="POL"),
        find_username("Board Member"),
    ],
)
def test_should_return_403_when_requesting_sv_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/2016-1-SVP-001" + extension,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("username", [find_username("Partner Affiliated User")])
def test_should_return_proposal_when_requesting_gwe_proposal_for_permitted_users(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2019-1-GWE-005",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["proposal_code"] == "2019-1-GWE-005"


@pytest.mark.parametrize("username", [find_username("Non-Partner Affiliated User")])
def test_should_return_403_when_requesting_gwe_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    for extension in ("", ".zip"):
        response = client.get(
            PROPOSALS_URL + "/2019-1-GWE-005" + extension,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_should_return_proposal_file(
    client: TestClient, tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    # Set up the proposal directory
    proposal_code = "2019-2-SCI-045"
    proposal_dir = tmp_path / proposal_code
    proposal_dir.mkdir()
    (proposal_dir / "1").mkdir()
    (proposal_dir / "2").mkdir()
    (proposal_dir / "3").mkdir()
    proposal_content = b"This is a proposal."
    proposal_file = proposal_dir / "3" / f"{proposal_code}.zip"
    proposal_file.write_bytes(proposal_content)

    class MockSettings(NamedTuple):
        proposals_dir: str

    def mock_get_settings() -> Any:
        return MockSettings(str(tmp_path))

    # Request the proposal file
    monkeypatch.setattr(
        "saltapi.service.proposal_service.get_settings", mock_get_settings
    )
    username = find_username("SALT Astronomer")
    authenticate(username, client)
    response = client.get(f"{PROPOSALS_URL}/{proposal_code}.zip")

    assert response.status_code == status.HTTP_200_OK
    assert response.content == proposal_content
    assert response.headers["Content-Type"] == "application/zip"
    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="{proposal_code}.zip"'
    )
