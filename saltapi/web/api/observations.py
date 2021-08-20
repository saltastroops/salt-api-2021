from typing import List

from fastapi import APIRouter, Path, Body

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.block import Block
from saltapi.web.schema.block import BlockVisitStatus, Observation

router = APIRouter(prefix="/observations", tags=["Observations"])


@router.get("/{block_id}", summary="Get observations of a block", response_model=Observation)
def get_observations(
        block_id: int = Path(
            ..., title="Block id", description="Unique identifier for a block of observations"
        )
) -> List[Observation]:
    """
    Returns observations of a given block id.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        block = block_repository.get(block_id)
        return block['observations']


@router.get("/{block_visit_id}/status", summary="Get observations' statuses of a block", response_model=BlockVisitStatus)
def get_observation_status(
        block_visit_id: int = Path(
            ..., title="Block id", description="Unique identifier for a block"
        )
) -> BlockVisitStatus:
    """
    Returns statuses of observations of a given block id.

    The following status values are possible.

    Status | Description
    --- | ---
    Accepted | The block is active
    Deleted | The block has been deleted.
    In queue | The proposal was submitted in a previous semester and will not be observed any longer.
    Rejected | The block currently is not in the queue and will not be observed.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        return block_repository.get_observation_status(block_visit_id)


@router.put("/{block_id}/status", summary="Update observations' statuses of a block")
def update_statuses_of_observations(
        block_visit_id: int = Path(
            ..., title="Block id", description="Unique identifier for a block"
        ),
        status: str = Body(
        ..., title="Block id", description="Unique identifier for a block"
        )
) -> Block:
    """
    Updates the status of observations with the given the block id. See the
    corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        instrument_repository = InstrumentRepository(unit_of_work.connection)
        target_repository = TargetRepository(unit_of_work.connection)
        block_repository = BlockRepository(
            instrument_repository=instrument_repository,
            target_repository=target_repository,
            connection=unit_of_work.connection,
        )
        block_repository.update_observation_status(block_visit_id, status)
