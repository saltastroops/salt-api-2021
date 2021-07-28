from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from saltapi.web.schema.common import TargetCoordinates, TimeInterval


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


class GuideStar(TargetCoordinates):
    """Guide star."""

    magnitude: float = Field(..., title="Magnitude", description="Magnitude")


class Lamp(str, Enum):
    """Calibration lamp(s)."""

    AR = "Ar"
    AR_AND_THAR = "Ar and ThAr"
    CUAR = "CuAr"
    CUAR_AND_XE = "CuAr and Xe"
    HGAR = "HgAr"
    HGAR_AND_NE = "HgAr and Ne"
    NE = "Ne"
    QTH1 = "QTH1"
    QTH1_AND_QTH2 = "QTH1 and QTH2"
    QTH2 = "QTH2"
    THAR = "ThAr"
    XE = "Xe"


class CalibrationFilter(str, Enum):
    """Calibration filter."""

    BLUE_AND_RED = "Blue and Red"
    CLEAR_AND_ND = "Clear and ND"
    CLEAR_AND_UV = "Clear and UV"
    ND_AND_CLEAR = "ND and Clear"
    NONE = "None"
    RED_AND_CLEAR = "Red and Clear"
    UV_AND_BLUE = "UV and Blue"


class GuideMethod(str, Enum):
    """Guide method."""

    HRS_PROBE = "HRS Probe"
    MANUAL = "Manual"
    NONE = "None"
    QUACK = "QUACK"
    RSS_PROBE = "RSS Probe"
    SALTICAM = "SALTICAM"
    SALTICAM_PROBE = "SALTICAM Probe"
    SLITVIEWER = "Slitviewer"


class PayloadConfigurationType(str, Enum):
    """Payload configuration type."""

    ACQUISITION = "Acquisition"
    CALIBRATION = "Calibration"
    INSTRUMENT_ACQUISITION = "Instrument Acquisition"
    SCIENCE = "Science"


class PayloadConfiguration(BaseModel):
    """Payload configuration."""

    payload_configuration_type: Optional[PayloadConfigurationType] = Field(
        ...,
        title="Payload configuration type",
        description="Payload configuration type",
    )
    use_calibration_screen: Optional[bool] = Field(
        ...,
        title="Calibration screen used?",
        description="Whether the calibration screen is used",
    )
    lamp: Optional[Lamp] = Field(
        ..., title="Calibration lamp", description="Calibration lamp"
    )
    calibration_filter: Optional[CalibrationFilter] = Field(
        ..., title="Calibration filter", description="Calibration filter"
    )
    guide_method: GuideMethod = Field(
        ..., title="Guide method", description="Guide method"
    )


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