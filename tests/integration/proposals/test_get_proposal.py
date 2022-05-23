import pytest
from fastapi.testclient import TestClient
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
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_should_return_404_when_requesting_non_existing_proposal(
    client: TestClient,
) -> None:
    username = find_username("administrator")
    proposal_code = "2020-2-SCI-099"
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/" + proposal_code,
        params={"proposal_code": proposal_code},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "username",
    [
        "ilkiewicz",  # Investigator
        "transients",  # Principal Contact
        "dibnob",  # Principal Investigator
        "nhlavutelo",  # Administrator
        "Nella",  # SALT Astronomer
        "nerasmus",  # TAC Member
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
        "ilkiewicz",  # Investigator
        "transients",  # Principal Contact
        "dibnob",  # Principal Investigator
        "jph",  # TAC Member,
        "tremonti",  # TAC Chair,
        "heinzs",  # Board Member
    ],
)
def test_should_return_403_when_requesting_science_proposal_for_non_permitted_users(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2019-2-SCI-006",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        "Srianand",  # Investigator
        "gitika",  # Principal Contact
        "ngupta",  # Principal Investigator
        "nhlavutelo",  # Administrator
        "Nella",  # SALT Astronomer
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
        "ajorisse",  # Investigator
        "Drisya",  # Principal Contact
        "rajeev",  # Principal Investigator
        "nerasmus",  # RSA TAC Member
        "mbackes",  # RSA TAC Chair
        "marek",  # POL TAC Member
        "tkastr",  # POL TAC Chair
        "heinzs",  # Board Member
    ],
)
def test_should_return_403_when_requesting_ddt_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2020-2-DDT-005",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        "eric",  # Investigator
        "eric",  # Principal Contact
        "eric",  # Principal Investigator
        "hettlage",  # Administrator
        "Nella",  # SALT Astronomer
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
        "ilkiewicz",  # Investigator
        "transients",  # Principal Contact
        "dibnob",  # Principal Investigator
        "nerasmus",  # RSA TAC Member
        "mbackes",  # RSA TAC Chair
        "marek",  # POL TAC Member
        "tkastr",  # POL TAC Chair
        "heinzs",  # Board Member
    ],
)
def test_should_return_403_when_requesting_com_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2016-1-COM-001",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "username",
    [
        "spotter",  # Investigator
        "khn",  # Principal Contact
        "crawford",  # Principal Investigator
        "hettlage",  # Administrator
        "Nella",  # SALT Astronomer
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
        "ilkiewicz",  # Investigator
        "transients",  # Principal Contact
        "dibnob",  # Principal Investigator
        "nerasmus",  # RSA TAC Member
        "mbackes",  # RSA TAC Chair
        "marek",  # POL TAC Member
        "tkastr",  # POL TAC Chair
        "heinzs",  # Board Member
    ],
)
def test_should_return_403_when_requesting_sv_proposal_for_non_permitted_user(
    username: str, client: TestClient
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/2016-1-SVP-001",
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
    response = client.get(
        PROPOSALS_URL + "/2019-1-GWE-005",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
