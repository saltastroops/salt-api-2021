from typing import List, Optional

from pydantic import BaseModel, Field

from saltapi.web.schema.common import TimeInterval


class PhaseInterval(BaseModel):
    """Phase interval."""

    start: float = Field(
        ..., title="Interval start", description="Start phase of the interval"
    )
    end: float = Field(
        ..., title="Interval end", description="End phase of the interval"
    )


class DitherPattern(BaseModel):
    """Dither pattern."""

    horizontal_tiles: int = Field(
        ...,
        title="Horizontal tiles",
        description="Number of horizontal tiles in the pattern",
        ge=1,
    )
    vertical_tiles: int = Field(
        ...,
        title="Horizontal tiles",
        description="Number of horizontal tiles in the pattern",
        ge=1,
    )
    offset_size: float = Field(
        ...,
        title="Offset size",
        description="Offset size, i.e. size of a dither step, in arcseconds",
    )
    steps: int = Field(..., title="Number of steps", description="Number of steps")
    description: str = Field(
        ...,
        title="Description",
        description="Human-friendly description of the dither pattern",
    )


class GuideStar(BaseModel):
    """Guide star."""

    right_ascension: float = Field(
        ...,
        title="Right ascension",
        description="Right ascension, in degrees",
        ge=0,
        le=360,
    )
    declination: float = Field(
        ..., tile="Declination", description="Declination, in degrees", ge=-90, le=90
    )
    equinox: float = Field(..., title="Equinox", description="Equinox", ge=0)
    magnitude: float = Field(..., title="Magnitude", description="Magnitude")


class PayloadConfiguration(BaseModel):
    """Payload configuration."""

    pass


class TelescopeConfiguration(BaseModel):
    """Telescope configuration."""

    iterations: int = Field(
        ...,
        title="Iterations",
        description="Number of iterations. This should usually be 1",
    )
    position_angle: float = Field(
        ...,
        title="Position angle",
        description="Position angle, measured from north to east, in degrees",
    )
    use_parallactic_angle: bool = Field(
        ...,
        title="Use parallactic angle?",
        description="Whether to use a parallactic angle",
    )
    dither_pattern: Optional[DitherPattern] = Field(
        ..., title="Dither pattern", description="Dither pattern"
    )
    guide_star: Optional[GuideStar] = Field(
        ..., title="Guide star", description="Guide star"
    )
    payload_configurations: List[PayloadConfiguration] = Field(
        ..., title="Payload configurations", description="Payload configurations"
    )


class Observation(BaseModel):
    """Observation."""

    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time required for executing the observation, including the overhead time, in seconds",
        gt=0,
    )
    overhead_time: int = Field(
        ..., title="Overhead time for the observation, in seconds", gt=0
    )
    time_restrictions: Optional[List[TimeInterval]] = Field(
        ...,
        title="Time restrictions",
        description="List of time intervals outside which the observation should not be made",
    )
    phase_constraints: Optional[List[PhaseInterval]] = Field(
        ...,
        title="Phase constraints",
        description="List of phase constraints. An observation should only be made when the phase of the (periodic) target is one of these intervals",
    )
    telescope_configurations: List[TelescopeConfiguration] = Field(
        ..., title="Telescope configurations", description="Telescope configurations"
    )
