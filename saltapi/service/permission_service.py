from saltapi.exceptions import AuthorizationError
from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.user_repository import UserRepository
from saltapi.service.proposal import ProposalCode
from saltapi.service.user import User


class PermissionService:
    def __init__(
        self,
        user_repository: UserRepository,
        proposal_repository: ProposalRepository,
        block_repository: BlockRepository,
    ) -> None:
        self.user_repository = user_repository
        self.proposal_repository = proposal_repository
        self.block_repository = block_repository

    def check_permission_to_view_proposal(
        self, user: User, proposal_code: ProposalCode
    ) -> None:
        """
        Check whether the user may view a proposal.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an investigator on the proposal
        * a TAC member for the proposal
        * an administrator
        """
        username = user.username
        proposal_type = self.proposal_repository.get_proposal_type(proposal_code)

        if proposal_type != "Gravitational Wave Event":
            may_view = (
                self.user_repository.is_salt_astronomer(username)
                or self.user_repository.is_investigator(username, proposal_code)
                or self.user_repository.is_tac_member_for_proposal(
                    username, proposal_code
                )
                or self.user_repository.is_administrator(username)
            )
        else:
            # Gravitational wave event proposals are a special case; they can be viewed
            # by anyone who belongs to a SALT partner.
            may_view = (
                self.user_repository.is_salt_astronomer(username)
                or self.user_repository.is_partner_affiliated_user(username)
                or self.user_repository.is_administrator(username)
            )

        if not may_view:
            raise AuthorizationError()

    def check_permission_to_activate_proposal(
        self, user: User, proposal_code: ProposalCode
    ) -> None:
        """
        Check whether the user may activate a proposal.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an activating investigator
        * an administrator
        """
        username = user.username

        may_activate = (
            (
                self.proposal_repository.is_self_activable(proposal_code)
                and (
                    self.user_repository.is_principal_investigator(
                        username, proposal_code
                    )
                    or self.user_repository.is_principal_contact(
                        username, proposal_code
                    )
                )
            )
            or self.user_repository.is_salt_astronomer(username)
            or self.user_repository.is_administrator(username)
        )

        if not may_activate:
            raise AuthorizationError()

    def check_permission_to_deactivate_proposal(
        self, user: User, proposal_code: ProposalCode
    ) -> None:
        """
        Check whether the user may deactivate a proposal.

        This is the case if the user is any of the following:

        * a Principal Investigator
        * a Principal Contact
        * a SALT Astronomer
        * an administrator
        """

        username = user.username

        may_deactivate = (
            self.user_repository.is_principal_investigator(username, proposal_code)
            or self.user_repository.is_principal_contact(username, proposal_code)
            or self.user_repository.is_salt_astronomer(username)
            or self.user_repository.is_administrator(username)
        )

        if not may_deactivate:
            raise AuthorizationError()

    def check_permission_to_update_proposal_status(self, user: User) -> None:
        """
        Check whether the user may update a proposal status.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an administrator
        """
        username = user.username

        may_update = self.user_repository.is_salt_astronomer(
            username
        ) or self.user_repository.is_administrator(username)

        if not may_update:
            raise AuthorizationError()

    def check_permission_to_view_block(self, user: User, block_id: int) -> None:
        """
        Check whether the user may view a block.

        This is the case if the user may view the proposal which the block belongs to.
        """
        proposal_code: ProposalCode = (
            self.block_repository.get_proposal_code_for_block_id(block_id)
        )

        self.check_permission_to_view_proposal(user, proposal_code)

    def check_permission_to_view_block_visit(
        self, user: User, block_visit_id: int
    ) -> None:
        """
        Check whether the user may view a block visit.

        This is the case if the user may view the proposal for which the block visit
        was taken.
        """
        proposal_code: ProposalCode = (
            self.block_repository.get_proposal_code_for_block_visit_id(block_visit_id)
        )

        self.check_permission_to_view_proposal(user, proposal_code)

    def check_permission_to_update_block_visit_status(self, user: User) -> None:
        """
        Check whether the user may update a block visit status.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an administrator
        """
        username = user.username

        may_update = self.user_repository.is_salt_astronomer(
            username
        ) or self.user_repository.is_administrator(username)

        if not may_update:
            raise AuthorizationError()

    def check_permission_to_view_user(self, user: User, updated_username: str) -> None:
        """
        Check whether the user may update a user.

        Administrators may view any users. Other users may only view their own user
        details.
        """

        if self.user_repository.is_administrator(user.username):
            may_view = True
        else:
            may_view = user.username == updated_username

        if not may_view:
            raise AuthorizationError()

    def check_permission_to_update_user(
        self, user: User, updated_username: str
    ) -> None:
        """
        Check whether the user may update a user.

        Administrators may update any users. Other users may only update their own user
        details.
        """

        if self.user_repository.is_administrator(user.username):
            may_update = True
        else:
            may_update = user.username == updated_username

        if not may_update:
            raise AuthorizationError()
