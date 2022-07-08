from sqlalchemy.engine import Connection

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.finder_chart_repository import FinderChartRepository
from saltapi.repository.institution_repository import InstitutionRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.block_service import BlockService
from saltapi.service.finder_chart_service import FinderChartService
from saltapi.service.institution_service import InstitutionService
from saltapi.service.instrument_service import InstrumentService
from saltapi.service.mail_service import MailService
from saltapi.service.permission_service import PermissionService
from saltapi.service.proposal_service import ProposalService
from saltapi.service.submission_service import SubmissionService
from saltapi.service.user_service import UserService


def authentication_service(connection: Connection) -> AuthenticationService:
    """Return an authentication service instance."""
    user_repository = UserRepository(connection)
    return AuthenticationService(user_repository)


def block_service(connection: Connection) -> BlockService:
    """Return a block service instance."""
    target_repository = TargetRepository(connection)
    instrument_repository = InstrumentRepository(connection)
    block_repository = BlockRepository(
        target_repository, instrument_repository, connection
    )
    return BlockService(block_repository)


def mail_service() -> MailService:
    """Return a mail service instance."""
    return MailService()


def permission_service(connection: Connection) -> PermissionService:
    """Return a permission service instance."""
    user_repository = UserRepository(connection)
    proposal_repository = ProposalRepository(connection)
    target_repository = TargetRepository(connection)
    instrument_repository = InstrumentRepository(connection)
    block_repository = BlockRepository(
        target_repository, instrument_repository, connection
    )
    return PermissionService(user_repository, proposal_repository, block_repository)


def proposal_service(connection: Connection) -> ProposalService:
    """Return a proposal service instance."""
    proposal_repository = ProposalRepository(connection)
    return ProposalService(proposal_repository)


def user_service(connection: Connection) -> UserService:
    """Return a user service instance."""
    user_repository = UserRepository(connection)
    return UserService(user_repository)


def instrument_service(connection: Connection) -> InstrumentService:
    """Return an instrument service instance."""
    instrument_repository = InstrumentRepository(connection)
    return InstrumentService(instrument_repository)


def institution_service(connection: Connection) -> InstitutionService:
    """Return an institution service instance."""
    institution_repository = InstitutionRepository(connection)
    return InstitutionService(institution_repository)


def submission_service(
    submission_repository: SubmissionRepository,
) -> SubmissionService:
    """Return a submission service instance."""
    return SubmissionService(submission_repository)


def finder_chart_service(connection: Connection) -> FinderChartService:
    """Return a finding chart service instance."""
    finding_chart_repository = FinderChartRepository(connection)
    return FinderChartService(finding_chart_repository)
