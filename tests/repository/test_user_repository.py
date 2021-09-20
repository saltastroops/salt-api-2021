from typing import Any, Callable, Optional, cast

import pytest
from pytest import MonkeyPatch
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


@nodatabase
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
            f"Should be true for investigator username '{investigator}, "
            f"proposal_code {proposal_code}"
        )


@nodatabase
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
            f"Should be false for non-investigator username '{non_investigator}, "
            f"proposal_code {proposal_code}"
        )


@nodatabase
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
    ), f"Should be true for PI username '{pi}', proposal code {proposal_code}"


@nodatabase
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
        assert not user_repository.is_principal_investigator(non_pi, proposal_code), (
            f"Should be false for non-PI username '{non_pi}', proposal code "
            f"{proposal_code}"
        )


@nodatabase
def test_is_principal_contact_returns_true_for_pc(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_contact"]
    proposal_code = data["proposal_code"]
    pc = data["principal_contact"]
    assert proposal_code
    assert pc
    user_repository = UserRepository(dbconnection)
    assert (
        user_repository.is_principal_contact(pc, proposal_code) is True
    ), f"Should be true for PC username '{pc}', proposal code {proposal_code}"


@nodatabase
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
        assert user_repository.is_principal_contact(non_pc, proposal_code) is False, (
            f"Should be false for non-PC username '{non_pc}', proposal code "
            f"{proposal_code}"
        )


@nodatabase
def test_is_salt_astronomer_returns_true_for_salt_astronomer(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_salt_astronomer"]
    salt_astronomers = data["salt_astronomers"]
    user_repository = UserRepository(dbconnection)
    for astronomer in salt_astronomers:
        assert user_repository.is_salt_astronomer(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_salt_astronomer_returns_false_for_salt_astronomer(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_salt_astronomer"]
    non_salt_astronomers = data["non_salt_astronomers"]
    user_repository = UserRepository(dbconnection)
    for astronomer in non_salt_astronomers:
        assert not user_repository.is_salt_astronomer(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_tac_member_returns_true_for_tac_member(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_member"]
    user_repository = UserRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["tac_members"]:
            assert user_repository.is_tac_member(
                username, proposal_code
            ), f"Should be true for {username} and {proposal_code}"


@nodatabase
def test_is_tac_member_returns_false_for_non_tac_member(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_member"]
    user_repository = UserRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["non_tac_members"]:
            assert not user_repository.is_tac_member(
                username, proposal_code
            ), f"Should be false for {username} and {proposal_code}"


@nodatabase
def test_is_tac_chair_returns_true_for_tac_chair(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_chair"]
    user_repository = UserRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["tac_chairs"]:
            assert user_repository.is_tac_chair(
                username, proposal_code
            ), f"Should be true for {username} and {proposal_code}"


@nodatabase
def test_is_tac_chair_returns_false_for_non_tac_chair(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_chair"]
    user_repository = UserRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["non_tac_chairs"]:
            assert not user_repository.is_tac_chair(
                username, proposal_code
            ), f"Should be false for {username} and {proposal_code}"


@nodatabase
def test_is_board_member_returns_true_for_board_member(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_board_member"]
    user_repository = UserRepository(dbconnection)
    for username in data["board_members"]:
        assert user_repository.is_board_member(
            username
        ), f"Should be true for {username}"


@nodatabase
def test_is_board_member_returns_false_for_non_board_member(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_board_member"]
    user_repository = UserRepository(dbconnection)
    for username in data["non_board_members"]:
        assert not user_repository.is_board_member(
            username
        ), f"Should be false for {username}"


@nodatabase
def test_is_administrator_returns_true_for_administrator(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_administrator"]
    administrators = data["administrators"]
    user_repository = UserRepository(dbconnection)
    for astronomer in administrators:
        assert user_repository.is_administrator(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_administrator_returns_false_for_administrator(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_administrator"]
    non_administrators = data["non_administrators"]
    user_repository = UserRepository(dbconnection)
    for astronomer in non_administrators:
        assert not user_repository.is_administrator(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
@pytest.mark.parametrize(
    "role",
    [
        "investigator",
        "principal_investigator",
        "principal_contact",
        "tac_member",
        "tac_chair",
    ],
)
def test_role_checks_return_false_for_non_existing_proposal(
    dbconnection: Connection, role: str
) -> None:
    user_repository = UserRepository(dbconnection)
    assert (
        getattr(user_repository, f"is_{role}")(
            username="gw", proposal_code="idontexist"
        )
        is False
    )


@nodatabase
def test_find_by_username_and_password_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any], monkeypatch: MonkeyPatch
) -> None:
    data = testdata(TEST_DATA_PATH)["find_user"]
    user_repository = UserRepository(dbconnection)

    # Allow any password
    monkeypatch.setattr(
        user_repository, "verify_password", lambda password, hashed_password: True
    )

    for expected_user in data:
        username = expected_user["username"]
        user = user_repository.find_user_with_username_and_password(
            username, "some_password"
        )

        assert user.id == expected_user["id"]
        assert user.username == username
        assert user.given_name == expected_user["given_name"]
        assert user.family_name == expected_user["family_name"]
        assert user.email == expected_user["email"]


@nodatabase
@pytest.mark.parametrize("username", ["idontexist", "", None])
def test_find_by_username_and_password_raises_error_for_wrong_username(
    dbconnection: Connection, username: Optional[str], monkeypatch: MonkeyPatch
) -> None:
    user_repository = UserRepository(dbconnection)

    # Allow any password
    monkeypatch.setattr(
        user_repository, "verify_password", lambda password, hashed_password: True
    )

    with pytest.raises(NotFoundError):
        user_repository.find_user_with_username_and_password(
            cast(str, username), "some_password"
        )


@nodatabase
def test_find_by_username_and_password_raises_error_for_wrong_password(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    user_repository = UserRepository(dbconnection)
    data = testdata(TEST_DATA_PATH)["find_user_with_wrong_password"]
    username = data["username"]

    # Make sure the author exists
    assert user_repository.get(username)

    with pytest.raises(NotFoundError):
        user_repository.find_user_with_username_and_password(username, "wrongpassword")

    with pytest.raises(NotFoundError):
        user_repository.find_user_with_username_and_password(username, "")

    # None may raise an exception other than NotFoundError
    with pytest.raises(Exception):
        user_repository.find_user_with_username_and_password(username, cast(str, None))
