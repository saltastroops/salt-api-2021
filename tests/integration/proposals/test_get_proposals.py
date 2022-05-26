import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import authenticate, find_username, not_authenticated

PROPOSALS_URL = "/proposals"


def test_should_return_401_when_requesting_proposals_for_unauthenticated_user(
    client: TestClient,
) -> None:
    not_authenticated(client)
    response = client.get(PROPOSALS_URL + "/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "from_semester, to_semester",
    [
        ("2022-1", "2021-2"),
        ("2020-1", "2019-2"),
        ("2022-2", "2020-1"),
    ],
)
def test_should_return_400_if_start_semester_later_than_end_semester(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = find_username("Administrator")
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "from_semester, to_semester",
    [
        ("abc", "2021-2"),
        ("2", "2019-2"),
        ("2022", "2020-1"),
        ("2020-1", "2021-3"),
        ("2020-1", "abc"),
    ],
)
def test_should_return_422_for_invalid_semesters(
    from_semester: str, to_semester: str, client: TestClient
) -> None:
    username = find_username("Administrator")
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={
            "from": from_semester,
            "to": to_semester,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "username,from_semester,to_semester,proposal_count,proposal_codes",
    [
        [
            find_username("TAC Chair", partner_code="RSA"),
            "2020-1",
            "2020-1",
            34,
            "many",
        ],
        [
            find_username("TAC Chair", partner_code="RU"),
            "2021-1",
            "2021-1",
            7,
            "2018-1-SCI-012, 2018-1-SCI-041, 2021-1-MLT-007, 2021-1-SCI-012, "
            "2021-1-SCI-015, 2021-1-SCI-028, 2021-1-SCI-031",
        ],
        [
            find_username("TAC Member", partner_code="UW"),
            "2021-1",
            "2021-1",
            8,
            "2018-2-LSP-001, 2018-2-MLT-005, 2020-1-MLT-005, 2020-1-MLT-009, "
            "2020-2-MLT-009, 2021-1-SCI-016, 2021-1-SCI-023, 2021-1-SCI-025",
        ],
        [
            find_username("Principal Investigator", proposal_code="2014-2-SCI-078"),
            "2020-2",
            "2020-2",
            0,
            "",
        ],
        [
            find_username("Principal Investigator", proposal_code="2018-2-LSP-001"),
            "2017-2",
            "2021-1",
            35,
            "many",
        ],
        [find_username("SALT Astronomer"), "2020-2", "2020-2", 81, "many"],
        [find_username("Administrator"), "2018-2", "2018-2", 79, "many"],
        [
            find_username("Principal Investigator", proposal_code="2014-2-SCI-078"),
            "2018-2",
            "2019-1",
            7,
            "many",
        ],
        [
            find_username("Principal Contact", proposal_code="2021-1-SCI-014"),
            "2018-2",
            "2019-1",
            0,
            "",
        ],
    ],
)
def test_should_return_correct_list_of_proposals_for_authenticated_user(
    username: str,
    from_semester: str,
    to_semester: str,
    proposal_count: int,
    proposal_codes: str,
    client: TestClient,
) -> None:
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL, params={"from": from_semester, "to": to_semester}
    )
    assert response.status_code == status.HTTP_200_OK

    # Proposals are returned
    proposals = response.json()
    for proposal in proposals:
        assert "proposal_code" in proposal
        assert "semester" in proposal
        assert "principal_investigator" in proposal

    # The number of proposals is correct
    assert len(proposals) == proposal_count

    # The proposal codes are correct
    if proposal_codes not in ("", "many"):
        assert set(p["proposal_code"] for p in proposals) == set(
            proposal_codes.split(", ")
        )


@pytest.mark.parametrize(
    "limit",
    [
        0,
        30,
        102,
    ],
)
def test_should_return_proposals_only_up_to_limit(
    limit: int, client: TestClient
) -> None:
    username = find_username("Administrator")
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={"limit": limit},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == limit


def test_should_return_422_for_invalid_limit(client: TestClient) -> None:
    username = find_username("Administrator")
    authenticate(username, client)
    response = client.get(
        PROPOSALS_URL + "/",
        params={"limit": -1},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_should_return_1000_proposals_as_the_default_limit(
    client: TestClient,
) -> None:
    username = find_username("Administrator")
    authenticate(username, client)
    response = client.get(PROPOSALS_URL + "/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1000
