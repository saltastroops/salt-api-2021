import uuid
from typing import Any, Callable, Optional, cast

import pytest
from pydantic import EmailStr
from pytest import MonkeyPatch
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.repository.user_repository import UserRepository
from saltapi.service.user import NewUserDetails, UserUpdate
from tests.markers import nodatabase

TEST_DATA_PATH = "repository/user_repository.yaml"


@nodatabase
def test_get_user_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user"]
    user_repository = UserRepository(dbconnection)
    user = user_repository.get_by_username(expected_user["username"])

    assert user.id == expected_user["id"]
    assert user.username == expected_user["username"]
    assert user.given_name == expected_user["given_name"]
    assert user.email is not None


@nodatabase
def test_get_user_raises_error_for_non_existing_user(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    with pytest.raises(NotFoundError):
        user_repository.get_by_username("idontexist")


@nodatabase
def test_get_user_by_id_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user_by_id"]
    user_repository = UserRepository(dbconnection)
    user = user_repository.get(expected_user["id"])

    assert user.id == expected_user["id"]
    assert user.username == expected_user["username"]
    assert user.email == expected_user["email"]
    assert user.given_name == expected_user["given_name"]
    assert user.family_name == expected_user["family_name"]
    assert user.password_hash is not None
    assert user.roles == expected_user["roles"]


@nodatabase
def test_get_user_by_email_returns_correct_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user_by_email"]
    user_repository = UserRepository(dbconnection)
    user = user_repository.get_by_email(expected_user["email"])

    assert user.id == expected_user["id"]
    assert user.username == expected_user["username"]
    assert user.email == expected_user["email"]
    assert user.given_name == expected_user["given_name"]
    assert user.family_name == expected_user["family_name"]
    assert user.password_hash is not None
    assert user.roles == expected_user["roles"]


def _random_string() -> str:
    return str(uuid.uuid4())[:8]


@nodatabase
def test_create_user_raisers_error_if_username_exists_already(
    dbconnection: Connection,
) -> None:
    username = "hettlage"
    new_user_details = NewUserDetails(
        username=username,
        primary_email=EmailStr(f"{username}@example.com"),
        email=[],
        given_name=_random_string(),
        family_name=_random_string(),
        password="very_secret",
        institute_id=5,
    )
    user_repository = UserRepository(dbconnection)
    with pytest.raises(ValueError) as excinfo:
        user_repository.create(new_user_details)

    assert "username" in str(excinfo.value).lower()


@nodatabase
def test_create_user_creates_a_new_user(dbconnection: Connection) -> None:
    username = _random_string()
    new_user_details = NewUserDetails(
        username=username,
        password=_random_string(),
        primary_email=EmailStr(f"{username}@example.com"),
        email=[""],
        given_name=_random_string(),
        family_name=_random_string(),
        institute_id=5,
    )

    user_repository = UserRepository(dbconnection)
    user_repository.create(new_user_details)

    created_user = user_repository.get_by_username(username)
    assert created_user.username == username
    assert created_user.password_hash is not None
    assert created_user.email == new_user_details.email
    assert created_user.given_name == new_user_details.given_name
    assert created_user.family_name == new_user_details.family_name
    assert created_user.roles == []


@nodatabase
def test_get_user_by_email_raises_error_for_non_existing_user(
    dbconnection: Connection,
) -> None:
    user_repository = UserRepository(dbconnection)
    with pytest.raises(NotFoundError):
        user_repository.get_by_username("invalid@email.com")


@nodatabase
def test_patch_raises_error_for_non_existing_user(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    with pytest.raises(NotFoundError):
        user_repository.update("idontexist", UserUpdate(username=None, password=None))


@nodatabase
def test_patch_uses_existing_values_by_default(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    username = "hettlage"
    old_user_details = user_repository.get_by_username(username)
    user_repository.update(username, UserUpdate(username=None, password=None))
    new_user_details = user_repository.get_by_username(username)

    assert old_user_details == new_user_details


def test_patch_replaces_existing_values(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    username = "hettlage"
    old_user_details = user_repository.get_by_username(username)

    new_username = "hettlage2"
    new_password = "a_new_shiny_password"
    assert not user_repository.verify_password(
        new_password, old_user_details.password_hash
    )

    user_repository.update(
        username, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details = user_repository.get_by_username(new_username)

    assert new_user_details.username == new_username
    assert user_repository.verify_password(new_password, new_user_details.password_hash)


def test_patch_is_idempotent(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    username = "hettlage"
    new_username = "hettlage2"
    new_password = "a_new_shiny_password"

    user_repository.update(
        username, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details_1 = user_repository.get_by_username(new_username)

    user_repository.update(
        new_username, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details_2 = user_repository.get_by_username(new_username)

    assert new_user_details_1 == new_user_details_2


def test_patch_cannot_use_existing_username(dbconnection: Connection) -> None:
    user_repository = UserRepository(dbconnection)
    username = "hettlage"
    existing_username = "nhlavutelo"

    with pytest.raises(ValueError):
        user_repository.update(
            username, UserUpdate(username=existing_username, password=None)
        )


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
            assert user_repository.is_tac_member_for_proposal(
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
            assert not user_repository.is_tac_member_for_proposal(
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
            assert user_repository.is_tac_chair_for_proposal(
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
            assert not user_repository.is_tac_chair_for_proposal(
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
def test_is_partner_affiliated_user_returns_true_for_affiliated_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_partner_affiliated_user"]
    user_repository = UserRepository(dbconnection)
    for username in data["affiliated_users"]:
        assert user_repository.is_partner_affiliated_user(
            username
        ), f"Should be true for {username}"


@nodatabase
def test_is_partner_affiliated_user_returns_false_for_non_affiliated_user(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_partner_affiliated_user"]
    user_repository = UserRepository(dbconnection)
    for username in data["non_affiliated_users"]:
        assert not user_repository.is_partner_affiliated_user(
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
        "tac_member_for_proposal",
        "tac_chair_for_proposal",
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

    # Make sure the user exists
    assert user_repository.get_by_username(username)

    with pytest.raises(NotFoundError):
        user_repository.find_user_with_username_and_password(username, "wrongpassword")

    with pytest.raises(NotFoundError):
        user_repository.find_user_with_username_and_password(username, "")

    # None may raise an exception other than NotFoundError
    with pytest.raises(Exception):
        user_repository.find_user_with_username_and_password(username, cast(str, None))


@nodatabase
def test_get_user_roles_returns_correct_roles(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["get_user_roles"]
    user_repository = UserRepository(dbconnection)
    for d in data:
        username = d["username"]
        expected_roles = set(d["roles"])
        roles = set(role.value for role in user_repository.get_user_roles(username))

        assert (
            expected_roles == roles
        ), f"Expected roles for {username}: {expected_roles}; found: {roles}"
