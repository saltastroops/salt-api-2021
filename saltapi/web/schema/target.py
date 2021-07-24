from typing import Optional

from pydantic import BaseModel, Field

from saltapi.web.schema.common import Ranking


class BaseTarget(BaseModel):
    """Base model for targets."""

    id: int = Field(
        ..., title="Target id", description="Unique identifier of the target"
    )
    name: str = Field(..., title="Target name", description="Target name")


class Phase1Target(BaseTarget):
    """A target in a Phase 1 proposal."""

    right_ascension: float = Field(
        ...,
        title="Right ascension",
        description="Right ascension, as an angle between 0 and 360 degrees (both inclusive)",
    )
    declination: float = Field(
        ...,
        title="Declination",
        description="Declination, as an angle between -90 and 90 degrees (both inclusive)",
    )
    equinox: float = Field(
        ...,
        title="Equinox",
        description="Equinox of the right ascension and declination",
    )
    horizons_identifier: Optional[str] = Field(
        ...,
        title="Horizons identifier",
        description="Identifier of the target in the Horizons database for solar system targets",
    )
    minimum_magnitude: float = Field(
        ..., title="Minimum magnitude", description="Minimum (brightest) magnitude"
    )
    maximum_magnitude: float = Field(
        ..., title="Maximum magnitude", description="Minimum (faintest) magnitude"
    )
    target_type: str = Field(
        ..., title="Target type", description="Target type (broad category)"
    )
    target_subtype: str = Field(
        ..., title="Target subtype", description="Target subtype"
    )
    is_optional: bool = Field(
        ...,
        title="Optional?",
        description="Whether the target is optional, i.e. whether it is part of a pool of targets from which only a subset needs to be observed.",
    )
    n_visits: int = Field(
        ...,
        title="Number of visits",
        description="Number of observations requested for the target",
    )
    max_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination",
        ge=0,
        le=100,
    )
    ranking: Ranking = Field(
        ...,
        title="Ranking",
        description="Importance attributed by the Principal Investigator to observations of this target relative to other observations for the same proposal.",
    )
    night_count: int = Field(
        ...,
        title="Number of nights",
        description="Number of nights for which the target is observable, given the requested observation time and observation constraints.",
    )
    # TODO: Comment on probabilities
    moon_probability: Optional[float]
    competition_probability: Optional[float]
    observability_probability: Optional[float]
    seeing_probability: Optional[float]
    average_ranking: Optional[float]
    total_probability: Optional[float]
