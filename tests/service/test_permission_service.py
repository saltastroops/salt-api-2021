from typing import Any, Iterable, List, Tuple, cast

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.proposal_repository import ProposalRepository
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
        is_tac_member_for_proposal: bool = False,
        is_tac_chair_for_proposal: bool = False,
        is_board_member: bool = False,
        is_partner_affiliated_user: bool = False,
        is_administrator: bool = False,
    ) -> None:
        self._is_investigator = is_investigator
        self._is_principal_investigator = is_principal_investigator
        self._is_principal_contact = is_principal_contact
        self._is_salt_astronomer = is_salt_astronomer
        self._is_tac_member = is_tac_member_for_proposal
        self._is_tac_chair = is_tac_chair_for_proposal
        self._is_board_member = is_board_member
        self._is_partner_affiliated_user = is_partner_affiliated_user
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

    def is_tac_member_for_proposal(
        self, username: str, proposal_code: ProposalCode
    ) -> bool:
        # A TAC chair is a TAC member as well
        return self._is_tac_member or self._is_tac_chair

    def is_tac_chair_for_proposal(
        self, username: str, proposal_code: ProposalCode
    ) -> bool:
        return self._is_tac_chair

    def is_board_member(self, username: str) -> bool:
        return self._is_board_member

    def is_partner_affiliated_user(self, username: str) -> bool:
        return self._is_partner_affiliated_user

    def is_administrator(self, username: str) -> bool:
        return self._is_administrator


class FakeProposalRepository:
    def __init__(self, is_self_activable: bool = False) -> None:
        self._is_self_activable = is_self_activable

    def is_self_activable(self, proposal_code: str) -> bool:
        return self._is_self_activable

    def get_proposal_type(self, proposal_code: str) -> str:
        return "Science " if "GW" not in proposal_code else "Gravitational Wave Event"


class FakeBlockRepository:
    pass


INVESTIGATOR = "investigator"
PRINCIPAL_INVESTIGATOR = "principal_investigator"
PRINCIPAL_CONTACT = "principal_contact"
SALT_ASTRONOMER = "salt_astronomer"
TAC_MEMBER_FOR_PROPOSAL = "tac_member_for_proposal"
TAC_CHAIR_FOR_PROPOSAL = "tac_chair_for_proposal"
BOARD_MEMBER = "board_member"
PARTNER_AFFILIATED_USER = "partner_affiliated_user"
ADMINISTRATOR = "administrator"

ALL_ROLES = {
    INVESTIGATOR,
    PRINCIPAL_INVESTIGATOR,
    PRINCIPAL_CONTACT,
    SALT_ASTRONOMER,
    TAC_MEMBER_FOR_PROPOSAL,
    TAC_CHAIR_FOR_PROPOSAL,
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


def _user_repositories_and_expected_results(
    roles_with_permission: Iterable[str],
) -> List[Tuple[str, UserRepository, bool]]:
    """
    Create a fake user repository for every role and return these along with the role
    and the expected result for a permission check. The latter is assumed to be True if
    and only if the role is in the given list of roles with permission.
    """
    values: List[Tuple[str, UserRepository, bool]] = []
    roles_without_permission = ALL_ROLES - set(roles_with_permission)

    # roles which have permission
    for role in roles_with_permission:
        kwargs = {f"is_{role}": True}
        user_repository = cast(UserRepository, FakeUserRepository(**kwargs))
        values.append((role, user_repository, True))

    # roles which don't have permission
    for role in roles_without_permission:
        kwargs = {f"is_{role}": False}
        user_repository = cast(UserRepository, FakeUserRepository(**kwargs))
        values.append((role, user_repository, False))

    return values


def _assert_role_based_permission(
    permission: str, roles_with_permission: List[str], **kwargs: Any
) -> None:
    """
    Check that a role has the given permission if and only if it is in the given list of
    roles.
    """
    proposal_repository = cast(ProposalRepository, FakeProposalRepository())
    block_repository = cast(BlockRepository, FakeBlockRepository)
    for (
        role,
        user_repository,
        expected_result,
    ) in _user_repositories_and_expected_results(roles_with_permission):
        permission_service = PermissionService(
            user_repository, proposal_repository, block_repository
        )
        assert (
            getattr(permission_service, permission)(user=USER, **kwargs)
            is expected_result
        ), f"Expected {expected_result} for {role}, got {not expected_result}"


def test_may_view_non_gravitational_wave_proposal() -> None:
    roles_with_permission = [
        INVESTIGATOR,
        PRINCIPAL_INVESTIGATOR,
        PRINCIPAL_CONTACT,
        SALT_ASTRONOMER,
        TAC_MEMBER_FOR_PROPOSAL,
        TAC_CHAIR_FOR_PROPOSAL,
        ADMINISTRATOR,
    ]
    _assert_role_based_permission(
        "may_view_proposal", roles_with_permission, proposal_code=PROPOSAL_CODE
    )


def test_may_view_gravitational_wave_proposal() -> None:
    roles_with_permission = [PARTNER_AFFILIATED_USER]
    _assert_role_based_permission(
        "may_view_proposal", roles_with_permission, proposal_code="2019-1-GWE-005"
    )


def test_may_update_proposal_status() -> None:
    roles_with_permission = [SALT_ASTRONOMER, ADMINISTRATOR]
    _assert_role_based_permission("may_update_proposal_status", roles_with_permission)


def test_may_activate_proposal() -> None:
    for role in ALL_ROLES:
        for is_self_activable in [True, False]:
            if role in [SALT_ASTRONOMER, ADMINISTRATOR]:
                expected_permitted = True
            elif (
                role in [PRINCIPAL_INVESTIGATOR, PRINCIPAL_CONTACT]
                and is_self_activable
            ):
                expected_permitted = True
            else:
                expected_permitted = False

            kwargs = {f"is_{role}": True}
            user_repository = cast(UserRepository, FakeUserRepository(**kwargs))
            proposal_repository = cast(
                ProposalRepository,
                FakeProposalRepository(is_self_activable=is_self_activable),
            )
            block_repository = cast(BlockRepository, FakeBlockRepository)
            permission_service = PermissionService(
                user_repository, proposal_repository, block_repository
            )

            assert (
                permission_service.may_activate_proposal(USER, PROPOSAL_CODE)
                == expected_permitted
            ), (
                f"Expected {expected_permitted} for role {role} and a "
                f"{'non-' if not is_self_activable else ''}self-activable proposal, "
                f"got {not expected_permitted}"
            )


def test_may_deactivate_proposal() -> None:
    roles_with_permission = [
        PRINCIPAL_INVESTIGATOR,
        PRINCIPAL_CONTACT,
        SALT_ASTRONOMER,
        ADMINISTRATOR,
    ]
    _assert_role_based_permission(
        "may_deactivate_proposal", roles_with_permission, proposal_code=PROPOSAL_CODE
    )
