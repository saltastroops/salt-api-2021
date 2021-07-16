from typing import Any, Callable

import pytest
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from tests.markers import nodatabase

TEST_DATA_PATH = "repository/user_repository.yaml"


@nodatabase
def test_get_user_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected = testdata(TEST_DATA_PATH)["get_user"]
    user_repository = UserRepository(dbconnection)
    user = user_repository.get(expected["username"])

    assert user.id == expected["id"]
    assert user.username == expected["username"]
    assert user.given_name == expected["given_name"]
    assert user.email is not None


@nodatabase
def test_get_user_raises_error_for_non_existing_user(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    with pytest.raises(NotFoundError):
        user_repository.get("idontexist")


def test_is_investigator_returns_true_for_investigator(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_investigator"]
    proposal_code = data["proposal_code"]
    investigators = data["investigators"]
    assert proposal_code
    assert len(investigators)
    user_repository = UserRepository(dbconnection)
    for investigator in investigators:
        assert user_repository.is_investigator(investigator, proposal_code), (
            f"True for investigator username '{investigator}, "
            f"proposal_code {proposal_code}"
        )


def test_is_investigator_returns_false_for_non_investigator(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_investigator"]
    proposal_code = data["proposal_code"]
    non_investigators = data["non_investigators"]
    assert proposal_code
    assert len(non_investigators)
    user_repository = UserRepository(dbconnection)
    for non_investigator in non_investigators:
        assert not user_repository.is_investigator(non_investigator, proposal_code), (
            f"False for non-investigator username '{non_investigator}, "
            f"proposal_code {proposal_code}"
        )


def test_is_principal_investigator_returns_true_for_pi(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_investigator"]
    proposal_code = data["proposal_code"]
    pi = data["principal_investigator"]
    assert proposal_code
    assert pi
    user_repository = UserRepository(dbconnection)
    assert user_repository.is_principal_investigator(
        pi, proposal_code
    ), f"True for PI username '{pi}', proposal code {proposal_code}"


def test_is_principal_investigator_returns_false_for_non_pi(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_investigator"]
    proposal_code = data["proposal_code"]
    non_pis = data["non_principal_investigators"]
    assert proposal_code
    assert len(non_pis)
    user_repository = UserRepository(dbconnection)
    for non_pi in non_pis:
        assert not user_repository.is_principal_investigator(
            non_pi, proposal_code
        ), f"True for non-PI username '{non_pi}', proposal code {proposal_code}"


def test_is_principal_contact_returns_true_for_pi(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_contact"]
    proposal_code = data["proposal_code"]
    pc = data["principal_contact"]
    assert proposal_code
    assert pc
    user_repository = UserRepository(dbconnection)
    assert user_repository.is_principal_contact(
        pc, proposal_code
    ), f"True for PC username '{pc}', proposal code {proposal_code}"


def test_is_principal_contact_returns_false_for_non_pc(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_contact"]
    proposal_code = data["proposal_code"]
    non_pcs = data["non_principal_contacts"]
    assert proposal_code
    assert len(non_pcs)
    user_repository = UserRepository(dbconnection)
    for non_pc in non_pcs:
        assert not user_repository.is_principal_contact(
            non_pc, proposal_code
        ), f"True for non-PC username '{non_pc}', proposal code {proposal_code}"
