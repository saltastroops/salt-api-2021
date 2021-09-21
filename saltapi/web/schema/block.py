from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from saltapi.web.schema.bvit import BvitSummary
from saltapi.web.schema.common import (
    BaseExecutedObservation,
    ObservationProbabilities,
    Priority,
    ProposalCode,
    Ranking,
    Semester,
    TimeInterval,
)
from saltapi.web.schema.hrs import HrsSummary
from saltapi.web.schema.observation import Observation
from saltapi.web.schema.rss import RssSummary
from saltapi.web.schema.salticam import SalticamSummary


class BlockStatusValue(str, Enum):
    """Block status value."""

    ACTIVE = "Active"
    COMPLETED = "Completed"
    DELETED = "Deleted"
    EXPIRED = "Expired"
    NOT_SET = "Not set"
    ON_HOLD = "On hold"
    SUPERSEDED = "Superseded"


class BlockStatus(BaseModel):
    value: BlockStatusValue = Field(
        ..., title="Block status value", description="Block status value"
    )
    reason: str = Field(
        ..., title="Block status reason", description="Block status reason"
    )


class BlockVisitStatus(str, Enum):
    """Block visit status."""

    ACCEPTED = "Accepted"
    #DELETED = "Deleted"
    IN_QUEUE = "In queue"
    REJECTED = "Rejected"


class Transparency(str, Enum):
    """Sky transparency."""

    ANY = "Any"
    CLEAR = "Clear"
    THICK_CLOUD = "Thick cloud"
    THIN_CLOUD = "Thin cloud"


class ObservingConditions(BaseModel):
    minimum_seeing: Optional[float] = Field(
        ...,
        title="Minimum seeing",
        description="Minimum seeing allowed for an observation, in arcseconds",
        ge=0,
    )
    maximum_seeing: float = Field(
        ...,
        title="Maximum seeing",
        description="Maximum seeing allowed for an observation, in arcseconds",
        ge=0,
    )
    transparency: Transparency = Field(
        ...,
        title="Transparency",
        description="Sky transparency required for an observation",
    )
    maximum_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination",
        ge=0,
        le=100,
    )
    minimum_lunar_distance: float = Field(
        ...,
        title="Minimum lunar distance",
        description="Minimum required angular distance between the Moon and the target, in degrees",
    )


class Block(BaseModel):
    """A block, i.e. a smallest schedulable unit in a proposal."""

    id: int = Field(..., title="Block id", description="Unique identifier of the block")
    name: Optional[str] = Field(..., title="Name", description="Block name")
    proposal_code: ProposalCode = Field(
        ..., title="Proposal code of the proposal to which the block belongs"
    )
    semester: Semester = Field(..., title="Semester to which the block belongs")
    status: BlockStatus = Field(..., title="Block status", description="Block status")
    priority: Priority = Field(
        ..., title="Priority", description="Priority of the block"
    )
    ranking: Optional[Ranking] = Field(
        ...,
        title="Ranking",
        description="Ranking by the Principal Investigator relative to other blocks in the proposal",
    )
    wait_period: int = Field(
        ...,
        title="Wait period",
        description="Minimum number of days to wait between observations of the block",
    )
    comment: Optional[str] = Field(
        ...,
        title="Comment",
        description="Comment about the block by the Principal Investigator",
    )
    requested_observations: int = Field(
        ...,
        title="Requested observations",
        description="Number of observations requested for the block",
    )
    executed_observations: List[BaseExecutedObservation] = Field(
        ...,
        title="Executed observations",
        description="Observations made for the block",
    )
    observing_conditions: ObservingConditions = Field(
        ...,
        title="Observing conditions",
        description="Conditions required for observing the block",
    )
    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time required for an observation of the block, including the overhead time, in seconds",
        gt=0,
    )
    overhead_time: Optional[int] = Field(
        ..., title="Overhead time for an observation of the block, in seconds", ge=0
    )
    observing_windows: List[TimeInterval] = Field(
        ...,
        title="Observing windows",
        description="Time windows during which the block can be observed",
    )
    observation_probabilities: ObservationProbabilities = Field(
        ...,
        title="Observing probabilities",
        description="Probabilities related to observing the block",
    )
    observations: List[Observation] = Field(
        ...,
        title="Observations",
        description="List of observations in the block. With the exception of some legacy proposals, there is always a single observation in the block",
    )


class BlockSummary(BaseModel):
    """Summary information about a block."""

    id: int = Field(
        ..., title="Block id", description="Unique identifier for the block"
    )
    name: str = Field(..., title="Name", description="Block name")
    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time required to make an observation of the block, in seconds",
        ge=0,
    )
    priority: Priority = Field(
        ..., title="Priority", description="Priority of the block"
    )
    requested_observations: int = Field(
        ...,
        title="Requested observations",
        description="Number of observations requested for the block",
    )
    accepted_observations: int = Field(
        ...,
        title="Accepted observations",
        description="Number of accepted observations made for the block so far",
    )
    rejected_observations: int = Field(
        ...,
        title="Rejected observations",
        description="Number of rejected observations made for the block so far",
    )
    is_observable_tonight: bool = Field(
        ...,
        title="Observable tonight?",
        description="Whether the block can be observed tonight (i.e. during the current Julian day)",
    )
    remaining_nights: int = Field(
        ...,
        title="Remaining nights",
        description="Number of nights (Julian days), excluding the current one, during which the block still can be observed",
    )
    observing_conditions: ObservingConditions = Field(
        ...,
        title="Observing conditions",
        description="Conditions required for observing the block",
    )
    instruments: List[
        Union[SalticamSummary, RssSummary, HrsSummary, BvitSummary]
    ] = Field(..., title="Instruments", description="Instruments used for the block")
