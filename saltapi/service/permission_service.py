from saltapi.repository.user_repository import UserRepository
from saltapi.service.proposal import ProposalCode
from saltapi.service.user import User


class PermissionService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def may_view_proposal(self, user: User, proposal_code: ProposalCode) -> bool:
        """
        Check whether the user may view a proposal.

        This is the case if the user is any of the following:

        * a SALT Astronomer
        * an investigator on the proposal
        * a TAC member for the proposal
        * a Board member
        * an administrator
        """
        username = user.username

        return (
            self.user_repository.is_salt_astronomer(username)
            or self.user_repository.is_investigator(username, proposal_code)
            or self.user_repository.is_tac_member(username, proposal_code)
            or self.user_repository.is_board_member(username)
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
            self.user_repository.is_activating_investigator(username, proposal_code)
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
