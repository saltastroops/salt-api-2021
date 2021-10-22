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

    def may_view_proposal(self, user: User, proposal_code: ProposalCode) -> bool:
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
            return (
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
            return (
                self.user_repository.is_salt_astronomer(username)
                or self.user_repository.is_partner_affiliated_user(username)
                or self.user_repository.is_administrator(username)
            )

    def may_activate_proposal(self, user: User, proposal_code: ProposalCode) -> bool:
        """
        Check whether the user may activate a proposal.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an activating investigator
        * an administrator
        """
        username = user.username

        return (
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

    def may_deactivate_proposal(self, user: User, proposal_code: ProposalCode) -> bool:
        """
        Check whether the user may deactivate a proposal.

        This is the case if the user is any of the following:

        * a Principal Investigator
        * a Principal Contact
        * a SALT Astronomer
        * an administrator
        """

        username = user.username

        return (
            self.user_repository.is_principal_investigator(username, proposal_code)
            or self.user_repository.is_principal_contact(username, proposal_code)
            or self.user_repository.is_salt_astronomer(username)
            or self.user_repository.is_administrator(username)
        )

    def may_update_proposal_status(self, user: User) -> bool:
        """
        Check whether the user may update a proposal status.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an administrator
        """
        username = user.username

        return self.user_repository.is_salt_astronomer(
            username
        ) or self.user_repository.is_administrator(username)

    def may_view_block(self, user: User, block_id: int) -> bool:
        """
        Check whether the user may view a block.

        This is the case if the user may view the proposal for which the block belongs to.
        """
        proposal_code: ProposalCode = (
            self.block_repository.get_proposal_code_for_block_id(block_id)
        )

        return self.may_view_proposal(user, proposal_code)

    def may_view_block_visit(self, user: User, block_visit_id: int) -> bool:
        """
        Check whether the user may view a block visit.

        This is the case if the user may view the proposal for which the block visit
        was taken.
        """
        proposal_code: ProposalCode = (
            self.block_repository.get_proposal_code_for_block_visit_id(block_visit_id)
        )

        return self.may_view_proposal(user, proposal_code)

    def may_update_block_visit_status(self, user: User) -> bool:
        """
        Check whether the user may update a block visit status.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an administrator
        """
        username = user.username

        return self.user_repository.is_salt_astronomer(
            username
        ) or self.user_repository.is_administrator(username)
