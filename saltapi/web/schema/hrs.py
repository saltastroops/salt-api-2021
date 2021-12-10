from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class HrsExposureType(str, Enum):
    """HRS exposure type."""

    ARC = "Arc"
    BIAS = "Bias"
    DARK = "Dark"
    FLAT_FIELD = "Flat Field"
    SCIENCE = "Science"
    SKY_FLAT = "Sky Flat"


class HrsIodineCellPosition(str, Enum):
    CALIBRATION = "Calibration"
    IN = "In"
    OUT = "Out"
    TH_AR_IN_SKY = "ThAr in sky fiber"
    TH_AR_IN_STAR = "ThAr in star fiber"


class HrsMode(str, Enum):
    """HRS modes."""

    HIGH_RESOLUTION = "High Resolution"
    HIGH_STABILITY = "High Stability"
    INT_CAL_FIBER = "Int Cal Fiber"
    LOW_RESOLUTION = "Low Resolution"
    MEDIUM_RESOLUTION = "Medium Resolution"


class HrsNodAndShuffle(BaseModel):
    """HRS nod and shuffle settings."""

    nod_interval: int = Field(
        ..., title="Nod interval", description="Time per nod interval, in seconds"
    )
    nod_count: int = Field(
        ..., title="Nod count", description="Number of nods required"
    )


class HrsTargetLocation(str, Enum):
    """HRS target location."""

    BISECT = "The star and sky fiber are equidistant from the optical axis"
    SKY = "The sky fiber is placed on the optical axis"
    STAR = "The star fiber is placed on the optical axis"


class HrsConfiguration(BaseModel):
    """HRS configuration."""

    mode: HrsMode = Field(..., title="Instrument mode", description="Instrument mode")
    exposure_type: HrsExposureType = Field(
        ..., title="Exposure type", description="Exposure type"
    )
    target_location: HrsTargetLocation
    fiber_separation: float = Field(..., title="Fiber separation, in arcseconds")
    iodine_cell_position: HrsIodineCellPosition = Field(
        ..., title="Iodine cell position", description="Iodine cell position"
    )
    is_th_ar_lamp_on: bool = Field(
        ..., title="ThAr lamp on?", description="Whether the ThAr lamp is on"
    )
    nod_and_shuffle: Optional[HrsNodAndShuffle] = Field(
        ..., title="Node and shuffle", description="Nod and shuffle settings"
    )


class HrsReadoutSpeed(str, Enum):
    FAST = "Fast"
    NONE = "None"
    SLOW = "Slow"


class HrsDetector(BaseModel):
    """HRS detector setup common to the red and blue detector."""

    pre_shuffled_rows: int = Field(
        ...,
        title="Pre-shuffled rows",
        description="Number of rows to shuffle before an exposure",
        ge=0,
    )
    post_shuffled_rows: int = Field(
        ...,
        title="Post-shuffled rows",
        description="Number of rows to shuffle before an exposure",
        ge=0,
    )
    pre_binned_rows: int = Field(
        ...,
        title="Pre-binned rows",
        description="Number of CCD rows to combine during readout",
        ge=1,
    )
    pre_binned_columns: int = Field(
        ...,
        title="Pre-binned columns",
        description="Number of CCD columns to combine during readout",
        ge=1,
    )
    iterations: int = Field(
        ..., title="Number of exposures", description="Number of exposures", ge=1
    )
    readout_speed: HrsReadoutSpeed = Field(
        ..., title="Readout speed", description="Readout speed"
    )


class HrsBlueDetector(HrsDetector):
    """HRS blue detector setup."""

    readout_amplifiers: Literal[1, 2] = Field(
        ...,
        title="Readout amplifiers",
        description="Number of amplifiers tyo be used during readout",
    )


class HrsRedDetector(HrsDetector):
    """HRS blue detector setup."""

    readout_amplifiers: Literal[1, 4] = Field(
        ...,
        title="Readout amplifiers",
        description="Number of amplifiers tyo be used during readout",
    )


class HrsProcedure(BaseModel):
    """HRS procedure."""

    cycles: int = Field(
        ...,
        title="Cycles",
        description="Number of cycles, i.e. how often to execute the procedure",
    )
    blue_exposure_times: List[Optional[float]] = Field(
        ...,
        title="Blue exposure times",
        description="Exposure times for the blue detector, in seconds",
    )
    red_exposure_times: List[Optional[float]] = Field(
        ...,
        title="Blue exposure times",
        description="Exposure times for the blue detector, in seconds",
    )


class Hrs(BaseModel):
    """An HRS setup."""

    id: int = Field(
        ..., title="HRS id", description="Unique identifier for the HRS setup"
    )
    configuration: HrsConfiguration = Field(
        ..., title="Instrument configuration", description="Instrument configuration"
    )
    blue_detector: HrsBlueDetector = Field(
        ..., title="Blue detector setup", description="Blue detector setup"
    )
    red_detector: HrsRedDetector = Field(
        ..., title="Red detector setup", description="Red detector setup"
    )
    procedure: HrsProcedure = Field(
        ..., title="Instrument procedure", description="Instrument procedure"
    )
    observation_time: float = Field(
        ...,
        title="Observation time",
        description="Total time required for the setup, in seconds",
        ge=0,
    )
    overhead_time: float = Field(
        ...,
        title="Overhead time",
        description="Overhead time for the setup, in seconds",
        ge=0,
    )


class HrsSummary(BaseModel):
    """Summary information for RSS."""

    name: Literal["HRS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[HrsMode] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
    grating: Optional[str] = Field(..., title="Grating", description="Grating")
