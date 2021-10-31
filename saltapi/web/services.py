from saltapi.repository.block_repository import BlockRepository
from sqlalchemy.engine import Connection

from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication_service import AuthenticationService
from saltapi.service.block_service import BlockService
from saltapi.service.mail_service import MailService
from saltapi.service.permission_service import PermissionService
from saltapi.service.user_service import UserService


def authentication_service(connection: Connection) -> AuthenticationService:
    """Return an authentication service instance."""
    user_repository = UserRepository(connection)
    return AuthenticationService(user_repository)


def block_service(connection: Connection) -> BlockService:
    """Return a block service instance."""
    target_repository = TargetRepository(connection)
    instrument_repository = InstrumentRepository(connection)
    block_repository = BlockRepository(target_repository, instrument_repository, connection)
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
    block_repository = BlockRepository(target_repository, instrument_repository, connection)
    return PermissionService(user_repository, proposal_repository, block_repository)


def user_service(connection: Connection) -> UserService:
    """Return a user service instance."""
    user_repository = UserRepository(connection)
    return UserService(user_repository)
