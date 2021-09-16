from typing import List, Dict, Any

from fastapi import APIRouter, Path, Body

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.observations_service import ObservationService
from saltapi.web.schema.block import BlockVisitStatus

router = APIRouter(prefix="/observations", tags=["Observations"])


@router.get("/{block_visit_id}", summary="Get observations", response_model=List[Dict[str, Any]])
def get_observations(
        block_visit_id: int = Path(
            ..., title="Block visit id", description="Unique identifier observations"
        )
) -> List[Dict[str, Any]]:
    """
    Returns observations of a given block visit id.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = BlockRepository(
            instrument_repository=InstrumentRepository(unit_of_work.connection),
            target_repository=TargetRepository(unit_of_work.connection),
            connection=unit_of_work.connection,
        )
        observation_service = ObservationService(block_repository)
        observations = observation_service.get_observations(block_visit_id)
        return observations


@router.get("/{block_visit_id}/status",
            summary="Get observations status",
            response_model=BlockVisitStatus)
def get_observations_status(
        block_visit_id: int = Path(
            ..., title="Block visit id", description="Unique identifier for observations"
        )
) -> BlockVisitStatus:
    """
    Returns the status of observations of a given block visit id.

    The following status values are possible.

    Status | Description
    --- | ---
    Accepted | The observations are accepted.
    Deleted | The observations has been deleted.
    In queue | The observations are in a queue.
    Rejected | The observations are rejected.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = BlockRepository(
            instrument_repository=InstrumentRepository(unit_of_work.connection),
            target_repository=TargetRepository(unit_of_work.connection),
            connection=unit_of_work.connection,
        )
        observation_service = ObservationService(block_repository)
        return observation_service.get_observations_status(block_visit_id)


@router.put("/{block_id}/status", summary="Update the status of observations")
def update_observations_status(
        block_visit_id: int = Path(
            ..., title="Block id", description="Unique identifier for a block visit"
        ),
        status: BlockVisitStatus = Body(
            ..., alias="status", title="Observations status", description="New observations status."
        )
) -> None:
    """
    Updates the status of observations with the given the block visit id.
    See the corresponding GET request for a description of the available status values.
    """

    with UnitOfWork() as unit_of_work:
        block_repository = BlockRepository(
            instrument_repository=InstrumentRepository(unit_of_work.connection),
            target_repository=TargetRepository(unit_of_work.connection),
            connection=unit_of_work.connection,
        )
        observation_service = ObservationService(block_repository)
        return observation_service.update_observations_status(block_visit_id, status)
