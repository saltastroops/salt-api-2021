from typing import Iterable, List, Tuple, cast

from saltapi.repository.user_repository import UserRepository
from saltapi.service.permission_service import PermissionService
from saltapi.service.proposal import ProposalCode
from saltapi.service.user import User


class FakeUserRepository:
    def __init__(
        self,
        is_investigator: bool = False,
        is_principal_investigator: bool = False,
        is_principal_contact: bool = False,
        is_salt_astronomer: bool = False,
        is_tac_member: bool = False,
        is_tac_chair: bool = False,
        is_board_member: bool = False,
        is_administrator: bool = False,
    ) -> None:
        self._is_investigator = is_investigator
        self._is_principal_investigator = is_principal_investigator
        self._is_principal_contact = is_principal_contact
        self._is_salt_astronomer = is_salt_astronomer
        self._is_tac_member = is_tac_member
        self._is_tac_chair = is_tac_chair
        self._is_board_member = is_board_member
        self._is_administrator = is_administrator

    def is_investigator(self, username: str, proposal_code: ProposalCode) -> bool:
        # A Principal Investigator or Contact is an investigator as well
        return (
            self._is_investigator
            or self._is_principal_investigator
            or self._is_principal_contact
        )

    def is_principal_investigator(
        self, username: str, proposal_code: ProposalCode
    ) -> bool:
        return self._is_principal_investigator

    def is_principal_contact(self, username: str, proposal_code: ProposalCode) -> bool:
        return self._is_principal_contact

    def is_salt_astronomer(self, username: str) -> bool:
        return self._is_salt_astronomer

    def is_tac_member(self, username: str, proposal_code: ProposalCode) -> bool:
        # A TAC chair is a TAC member as well
        return self._is_tac_member or self._is_tac_chair

    def is_tac_chair(self, username: str, proposal_code: ProposalCode) -> bool:
        return self._is_tac_chair

    def is_board_member(self, username: str) -> bool:
        return self._is_board_member

    def is_administrator(self, username: str) -> bool:
        return self._is_administrator


INVESTIGATOR = "investigator"
PRINCIPAL_INVESTIGATOR = "principal_investigator"
PRINCIPAL_CONTACT = "principal_contact"
SALT_ASTRONOMER = "salt_astronomer"
TAC_MEMBER = "tac_member"
TAC_CHAIR = "tac_chair"
BOARD_MEMBER = "board_member"
ADMINISTRATOR = "administrator"

ALL_ROLES = {
    INVESTIGATOR,
    PRINCIPAL_INVESTIGATOR,
    PRINCIPAL_CONTACT,
    SALT_ASTRONOMER,
    TAC_MEMBER,
    TAC_CHAIR,
    BOARD_MEMBER,
    ADMINISTRATOR,
}

USER = User(
    id=42,
    username="someone",
    given_name="Some",
    family_name="One",
    email="someone@example.com",
    password_hash="1234",
)

PROPOSAL_CODE = ProposalCode("some_code")


def _repositories_and_expected_results(
    roles_with_permission: Iterable[str],
) -> List[Tuple[str, UserRepository, bool]]:
    values: List[Tuple[str, UserRepository, bool]] = []
    roles_without_permission = ALL_ROLES - set(roles_with_permission)
    for role in roles_with_permission:
        kwargs = {f"is_{role}": True}
        user_repository = cast(UserRepository, FakeUserRepository(**kwargs))
        values.append((role, user_repository, True))
    for role in roles_without_permission:
        kwargs = {role: False}
        user_repository = cast(UserRepository, FakeUserRepository(**kwargs))
        values.append((role, user_repository, False))

    return values


def test_may_view_proposal() -> None:
    roles_with_permission = [
        INVESTIGATOR,
        PRINCIPAL_INVESTIGATOR,
        PRINCIPAL_CONTACT,
        SALT_ASTRONOMER,
        TAC_MEMBER,
        TAC_CHAIR,
        BOARD_MEMBER,
        ADMINISTRATOR,
    ]
    for role, repository, expected_result in _repositories_and_expected_results(
        roles_with_permission
    ):
        permission_service = PermissionService(repository)
        assert permission_service.may_view_proposal(
            USER, PROPOSAL_CODE
        ), f"Expected {expected_result} for {role}, got {not expected_result}"
