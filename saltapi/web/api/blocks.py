import requests
from fastapi import APIRouter, Body, Depends, Path
from xml.dom import minidom

from saltapi.exceptions import AuthorizationError
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.block import Block as _Block
from saltapi.service.block import BlockStatus as _BlockStatus
from saltapi.service.user import User, Role
from saltapi.settings import get_settings
from saltapi.web import services
from saltapi.web.schema.block import Block, BlockStatus, BlockStatusValue

router = APIRouter(prefix="/blocks", tags=["Block"])


@router.get(
    "/scheduled-block", summary="Scheduled block.", response_model=Block
)
def get_scheduled_block(user: User = Depends(get_current_user)) -> _Block:
    """

    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        block_service = services.block_service(unit_of_work.connection)
        if permission_service.check_user_has_role(user, Role.ADMINISTRATOR) \
                or permission_service.check_user_has_role(user, Role.SALT_ASTRONOMER) \
                or permission_service.check_user_has_role(user, Role.SALT_OPERATOR):
            file = requests.get(get_settings().tcs_icd)
            xml_file = minidom.parseString(file.text)
            models = xml_file.getElementsByTagName('String')
            block_id = None
            for els in models:
                # This will give a NodeList item
                name = els.getElementsByTagName('Name')
                # Which needs to be converted to a DOM Element by calling item(0)
                if name.item(0).firstChild.data == "block id":
                    value = els.getElementsByTagName('Val')
                    block_id = value.item(0).firstChild.data
            if not block_id:
                raise FileNotFoundError()
            return block_service.get_block(block_id)
        raise AuthorizationError()


@router.get(
    "/next-scheduled-block", summary="Scheduled block.", response_model=Block
)
def get_next_scheduled_block(user: User = Depends(get_current_user)) -> _Block:
    """
    Get next scheduled block.
    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        block_service = services.block_service(unit_of_work.connection)
        if permission_service.check_user_has_role(user, Role.ADMINISTRATOR) \
                or permission_service.check_user_has_role(user, Role.SALT_ASTRONOMER) \
                or permission_service.check_user_has_role(user, Role.SALT_OPERATOR):

            return block_service.get_next_scheduled_block()
        raise AuthorizationError()


@router.get("/{block_id}", summary="Get a block", response_model=Block)
def get_block(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    user: User = Depends(get_current_user),
) -> _Block:
    """
    Returns the block with a given id.
    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_block(user, block_id)

        block_service = services.block_service(unit_of_work.connection)
        return block_service.get_block(block_id)


@router.get(
    "/{block_id}/status", summary="Get a block status", response_model=BlockStatus
)
def get_block_status(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    user: User = Depends(get_current_user),
) -> _BlockStatus:
    """
    Returns the status of the block with a given block id.

    The status is described by a status value and a reason for that value.
    The following status values are possible.

    Status | Description
    --- | ---
    Active | The block is active.
    Completed | The block has been completed.
    Deleted | The block has been deleted.
    Expired | The block was submitted in a previous semester and will not be observed any longer.
    Not set | The block status currently is not set.
    On hold | The block is currently on hold.
    Superseded | The block has been superseded. This is a legacy status that should not be used any longer.
    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_block_status(user, block_id)

        block_service = services.block_service(unit_of_work.connection)
        return block_service.get_block_status(block_id)


@router.put(
    "/{block_id}/status", summary="Update a block status", response_model=BlockStatus
)
def update_block_status(
    block_id: int = Path(
        ..., title="Block id", description="Unique identifier for the block"
    ),
    block_status: BlockStatusValue = Body(
        ..., alias="status", title="Block status", description="New block status."
    ),
    status_reason: str = Body(
        ...,
        alias="reason",
        title="Block status reason",
        description="New block status reason.",
    ),
    user: User = Depends(),
) -> _BlockStatus:
    """
    Updates the status of the block with the given the block id.
    See the corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_block_status(user, block_id)

        block_service = services.block_service(unit_of_work.connection)
        block_service.update_block_status(block_id, block_status, status_reason)

        return block_service.get_block_status(block_id)
