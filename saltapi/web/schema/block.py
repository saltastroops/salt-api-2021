from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from saltapi.web.schema.bvit import BvitSummary
from saltapi.web.schema.common import (
    BaseExecutedObservation,
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


class Transparency(str, Enum):
    """Sky transparency."""

    ANY = "Any"
    CLEAR = "Clear"
    THICK_CLOUD = "Thick cloud"
    THIN_CLOUD = "Thin cloud"


class InstrumentSummary(BaseModel):
    """Summary details of an instrument setup."""

    name: str = Field(..., title="Name", description="Instrument name")
    mode: str = Field(
        ...,
        title="Mode",
        description="Instrument mode. For Salticam this is just an empty string.",
    )


class BlockStatus(str, Enum):
    """Block status."""

    ACTIVE = "Active"
    COMPLETED = "Completed"
    DELETED = "Deleted"
    EXPIRED = "Expired"
    NOT_SET = "Not set"
    ON_HOLD = "On Hold"
    SUPERSEDED = "Superseded"


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
    instruments: List[
        Union[SalticamSummary, RssSummary, HrsSummary, BvitSummary]
    ] = Field(..., title="Instruments", description="Instruments used for the block")


class Block(BaseModel):
    """A block, i.e. a smallest schedulable unit in a proposal."""

    block_id: int = Field(
        ..., title="Block id", description="Unique identifier of the block"
    )
    name: str = Field(..., title="Name", description="Block name")
    proposal_code: ProposalCode = Field(
        ..., title="Proposal code of the proposal to which the block belongs"
    )
    semester: Semester = Field(..., title="Semester to which the block belongs")
    status: BlockStatus = Field(..., title="Block status", description="Block status")
    priority: Priority = Field(
        ..., title="Priority", description="Priority of the block"
    )
    ranking: Ranking = Field(
        ...,
        title="Ranking",
        description="Ranking by the Principal Investigator relative to other blocks in the proposal",
    )
    wait_period: int = Field(
        ...,
        title="Wait period",
        description="Minimum number of days to wait between observations of the block",
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
    minimum_seeing: float = Field(
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
    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time required for an observation of the block, including the overhead time, in seconds",
        gt=0,
    )
    shutter_open_time: int = Field(
        ...,
        title="Shutter open time",
        description="Total exposure time for an observation of the block, in seconds",
    )
    overhead_time: int = Field(
        ..., title="Overhead time for an observation of the block, in seconds", gt=0
    )
    observing_windows: List[TimeInterval] = Field(
        ...,
        title="Observing windows",
        description="Time windows during which the block can be observed",
    )
    moon_probability: Optional[float] = Field(
        ...,
        title="Moon probability",
        description="Moon probability, which is derived from the lunar phase cumulative distribution function during the semester. The moon probability is not used in the total probability calculation since the moon constraints are already incorporated in the visibility window calculations",
    )
    competition_probability: Optional[float] = Field(
        ...,
        title="Competition probability",
        description="Competition probability, which is determined as P_comp(x) = 1 / (C + 1) where C is the number of targets that overlap with target x",
        ge=0,
        le=1,
    )
    observability_probability: Optional[float] = Field(
        ...,
        title="Observability probability",
        description="Probability representing the likelihood of pointing to a target given the length of its visibility window and the time requested on target. The probability is represented by the ratio of the length of the observing window and the length of the visibility window",
        ge=0,
        le=1,
    )
    seeing_probability: Optional[float] = Field(
        ...,
        title="Seeing probability",
        description="Seeing probability, whivh is derived from the cumulative distribution function of seeing measurements taken in Sutherland",
        ge=0,
        le=1,
    )
    average_ranking: Optional[float] = Field(
        ..., title="Average ranking", description="Average ranking", ge=0
    )
    total_probability: Optional[float] = Field(
        ...,
        title="Total probability",
        description="Total probability, which is derived using the binomial theorem, where the number of trials are the number of tracks available to observe a target, the number of successes is the number of visits requested and the probability per trial is the total probability per track",
        ge=0,
        le=1,
    )
    observations: List[Observation] = Field(
        ...,
        title="Observations",
        description="List of observations in the block. With the exception of some legacy proposals, there is always a single observation in the block",
    )
