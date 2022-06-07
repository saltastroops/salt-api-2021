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
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user"]
    user_repository = UserRepository(db_connection)
    user = user_repository.get_by_username(expected_user["username"])

    assert user.id == expected_user["id"]
    assert user.username == expected_user["username"]
    assert user.given_name == expected_user["given_name"]
    assert user.email is not None


@nodatabase
def test_get_user_raises_error_for_non_existing_user(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    with pytest.raises(NotFoundError):
        user_repository.get_by_username("idontexist")


@nodatabase
def test_get_user_by_id_returns_correct_user(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user_by_id"]
    user_repository = UserRepository(db_connection)
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
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    expected_user = testdata(TEST_DATA_PATH)["get_user_by_email"]
    user_repository = UserRepository(db_connection)
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
    db_connection: Connection,
) -> None:
    username = "hettlage"
    new_user_details = NewUserDetails(
        username=username,
        email=EmailStr(f"{username}@example.com"),
        alternative_emails=[],
        given_name=_random_string(),
        family_name=_random_string(),
        password="very_secret",
        institution_id=5,
    )
    user_repository = UserRepository(db_connection)
    with pytest.raises(ValueError) as excinfo:
        user_repository.create(new_user_details)

    assert "username" in str(excinfo.value).lower()


@nodatabase
def test_create_user_creates_a_new_user(db_connection: Connection) -> None:
    username = _random_string()
    new_user_details = NewUserDetails(
        username=username,
        password=_random_string(),
        email=EmailStr(f"{username}@example.com"),
        alternative_emails=[],
        given_name=_random_string(),
        family_name=_random_string(),
        institution_id=5,
    )

    user_repository = UserRepository(db_connection)
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
    db_connection: Connection,
) -> None:
    user_repository = UserRepository(db_connection)
    with pytest.raises(NotFoundError):
        user_repository.get_by_username("invalid@email.com")


@nodatabase
def test_patch_raises_error_for_non_existing_user(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    with pytest.raises(NotFoundError):
        user_repository.update(0, UserUpdate(username=None, password=None))


@nodatabase
def test_patch_uses_existing_values_by_default(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    user_id = 1602
    old_user_details = user_repository.get(user_id)
    user_repository.update(user_id, UserUpdate(username=None, password=None))
    new_user_details = user_repository.get(user_id)

    assert old_user_details == new_user_details


def test_patch_replaces_existing_values(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    user_id = 1602
    old_user_details = user_repository.get(user_id)

    new_username = "hettlage2"
    new_password = "a_new_shiny_password"
    assert not user_repository.verify_password(
        new_password, old_user_details.password_hash
    )

    user_repository.update(
        user_id, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details = user_repository.get(user_id)

    assert new_user_details.username == new_username
    assert user_repository.verify_password(new_password, new_user_details.password_hash)


def test_patch_is_idempotent(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    user_id = 1602
    new_username = "hettlage2"
    new_password = "a_new_shiny_password"

    user_repository.update(
        user_id, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details_1 = user_repository.get_by_username(new_username)

    user_repository.update(
        user_id, UserUpdate(username=new_username, password=new_password)
    )
    new_user_details_2 = user_repository.get_by_username(new_username)

    assert new_user_details_1 == new_user_details_2


def test_patch_cannot_use_existing_username(db_connection: Connection) -> None:
    user_repository = UserRepository(db_connection)
    user_id = 1602
    existing_username = "nhlavutelo"

    with pytest.raises(ValueError):
        user_repository.update(
            user_id, UserUpdate(username=existing_username, password=None)
        )


@nodatabase
def test_is_investigator_returns_true_for_investigator(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_investigator"]
    proposal_code = data["proposal_code"]
    investigators = data["investigators"]
    assert proposal_code
    assert len(investigators)
    user_repository = UserRepository(db_connection)
    for investigator in investigators:
        assert user_repository.is_investigator(investigator, proposal_code), (
            f"Should be true for investigator username '{investigator}, "
            f"proposal_code {proposal_code}"
        )


@nodatabase
def test_is_investigator_returns_false_for_non_investigator(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_investigator"]
    proposal_code = data["proposal_code"]
    non_investigators = data["non_investigators"]
    assert proposal_code
    assert len(non_investigators)
    user_repository = UserRepository(db_connection)
    for non_investigator in non_investigators:
        assert not user_repository.is_investigator(non_investigator, proposal_code), (
            f"Should be false for non-investigator username '{non_investigator}, "
            f"proposal_code {proposal_code}"
        )


@nodatabase
def test_is_principal_investigator_returns_true_for_pi(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_investigator"]
    proposal_code = data["proposal_code"]
    pi = data["principal_investigator"]
    assert proposal_code
    assert pi
    user_repository = UserRepository(db_connection)
    assert user_repository.is_principal_investigator(
        pi, proposal_code
    ), f"Should be true for PI username '{pi}', proposal code {proposal_code}"


@nodatabase
def test_is_principal_investigator_returns_false_for_non_pi(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_investigator"]
    proposal_code = data["proposal_code"]
    non_pis = data["non_principal_investigators"]
    assert proposal_code
    assert len(non_pis)
    user_repository = UserRepository(db_connection)
    for non_pi in non_pis:
        assert not user_repository.is_principal_investigator(non_pi, proposal_code), (
            f"Should be false for non-PI username '{non_pi}', proposal code "
            f"{proposal_code}"
        )


@nodatabase
def test_is_principal_contact_returns_true_for_pc(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_contact"]
    proposal_code = data["proposal_code"]
    pc = data["principal_contact"]
    assert proposal_code
    assert pc
    user_repository = UserRepository(db_connection)
    assert (
        user_repository.is_principal_contact(pc, proposal_code) is True
    ), f"Should be true for PC username '{pc}', proposal code {proposal_code}"


@nodatabase
def test_is_principal_contact_returns_false_for_non_pc(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_principal_contact"]
    proposal_code = data["proposal_code"]
    non_pcs = data["non_principal_contacts"]
    assert proposal_code
    assert len(non_pcs)
    user_repository = UserRepository(db_connection)
    for non_pc in non_pcs:
        assert user_repository.is_principal_contact(non_pc, proposal_code) is False, (
            f"Should be false for non-PC username '{non_pc}', proposal code "
            f"{proposal_code}"
        )


@nodatabase
def test_is_salt_astronomer_returns_true_for_salt_astronomer(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_salt_astronomer"]
    salt_astronomers = data["salt_astronomers"]
    user_repository = UserRepository(db_connection)
    for astronomer in salt_astronomers:
        assert user_repository.is_salt_astronomer(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_salt_astronomer_returns_false_for_salt_astronomer(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_salt_astronomer"]
    non_salt_astronomers = data["non_salt_astronomers"]
    user_repository = UserRepository(db_connection)
    for astronomer in non_salt_astronomers:
        assert not user_repository.is_salt_astronomer(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_tac_member_returns_true_for_tac_member(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_member"]
    user_repository = UserRepository(db_connection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["tac_members"]:
            assert user_repository.is_tac_member_for_proposal(
                username, proposal_code
            ), f"Should be true for {username} and {proposal_code}"


@nodatabase
def test_is_tac_member_returns_false_for_non_tac_member(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_member"]
    user_repository = UserRepository(db_connection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["non_tac_members"]:
            assert not user_repository.is_tac_member_for_proposal(
                username, proposal_code
            ), f"Should be false for {username} and {proposal_code}"


@nodatabase
def test_is_tac_chair_returns_true_for_tac_chair(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_chair"]
    user_repository = UserRepository(db_connection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["tac_chairs"]:
            assert user_repository.is_tac_chair_for_proposal(
                username, proposal_code
            ), f"Should be true for {username} and {proposal_code}"


@nodatabase
def test_is_tac_chair_returns_false_for_non_tac_chair(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_tac_chair"]
    user_repository = UserRepository(db_connection)
    for d in data:
        proposal_code = d["proposal_code"]

        for username in d["non_tac_chairs"]:
            assert not user_repository.is_tac_chair_for_proposal(
                username, proposal_code
            ), f"Should be false for {username} and {proposal_code}"


@nodatabase
def test_is_board_member_returns_true_for_board_member(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_board_member"]
    user_repository = UserRepository(db_connection)
    for username in data["board_members"]:
        assert user_repository.is_board_member(
            username
        ), f"Should be true for {username}"


@nodatabase
def test_is_board_member_returns_false_for_non_board_member(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_board_member"]
    user_repository = UserRepository(db_connection)
    for username in data["non_board_members"]:
        assert not user_repository.is_board_member(
            username
        ), f"Should be false for {username}"


@nodatabase
def test_is_partner_affiliated_user_returns_true_for_affiliated_user(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_partner_affiliated_user"]
    user_repository = UserRepository(db_connection)
    for username in data["affiliated_users"]:
        assert user_repository.is_partner_affiliated_user(
            username
        ), f"Should be true for {username}"


@nodatabase
def test_is_partner_affiliated_user_returns_false_for_non_affiliated_user(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_partner_affiliated_user"]
    user_repository = UserRepository(db_connection)
    for username in data["non_affiliated_users"]:
        assert not user_repository.is_partner_affiliated_user(
            username
        ), f"Should be false for {username}"


@nodatabase
def test_is_administrator_returns_true_for_administrator(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_administrator"]
    administrators = data["administrators"]
    user_repository = UserRepository(db_connection)
    for astronomer in administrators:
        assert user_repository.is_administrator(
            astronomer
        ), f"Should be true for {astronomer}"


@nodatabase
def test_is_administrator_returns_false_for_administrator(
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["is_administrator"]
    non_administrators = data["non_administrators"]
    user_repository = UserRepository(db_connection)
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
    db_connection: Connection, role: str
) -> None:
    user_repository = UserRepository(db_connection)
    assert (
        getattr(user_repository, f"is_{role}")(
            username="gw", proposal_code="idontexist"
        )
        is False
    )


@nodatabase
def test_find_by_username_and_password_returns_correct_user(
    db_connection: Connection, testdata: Callable[[str], Any], monkeypatch: MonkeyPatch
) -> None:
    data = testdata(TEST_DATA_PATH)["find_user"]
    user_repository = UserRepository(db_connection)

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
    db_connection: Connection, username: Optional[str], monkeypatch: MonkeyPatch
) -> None:
    user_repository = UserRepository(db_connection)

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
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    user_repository = UserRepository(db_connection)
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
    db_connection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA_PATH)["get_user_roles"]
    user_repository = UserRepository(db_connection)
    for d in data:
        username = d["username"]
        expected_roles = set(d["roles"])
        roles = set(role.value for role in user_repository.get_user_roles(username))

        assert (
            expected_roles == roles
        ), f"Expected roles for {username}: {expected_roles}; found: {roles}"
