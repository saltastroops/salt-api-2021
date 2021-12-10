from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SalticamDetectorMode(str, Enum):
    """Salticam detector mode."""

    DRIFT_SCAN = "Drift Scan"
    FRAME_TRANSFER = "Frame Transfer"
    NORMAL = "Normal"
    SLOT_MODE = "Slot Mode"


class SalticamDetectorWindow(BaseModel):
    """Salticam detector window."""

    center_right_ascension: float = Field(
        ...,
        title="Center right ascension",
        description="Right ascension of the detector window center, in degrees",
    )
    center_declination: float = Field(
        ...,
        title="Center declination",
        description="Declination of the detector window center, in degrees",
    )
    height: int = Field(
        ..., title="Height", description="Height of the detector window, in arcseconds"
    )
    width: int = Field(
        ..., title="Width", description="Width of the detector window, in arcseconds"
    )


class SalticamExposureType(str, Enum):
    """Salticam exposure type."""

    BIAS = "Bias"
    FLAT_FIELD = "Flat Field"
    SCIENCE = "Science"


class SalticamGain(str, Enum):
    """Salticam gain."""

    BRIGHT = "Bright"
    FAINT = "Faint"


class SalticamReadoutSpeed(str, Enum):
    """Salticam readout speed."""

    FAST = "Fast"
    NONE = "None"
    SLOW = "Slow"


class SalticamDetector(BaseModel):
    """Salticam detector setup."""

    mode: SalticamDetectorMode = Field(
        ..., title="Detector mode", description="Detector mode"
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
        ...,
        title="Number of exposures",
        description="Number of exposures per procedure step",
        ge=1,
    )
    exposure_type: SalticamExposureType = Field(
        ..., title="Exposure type", description="Exposure type"
    )
    gain: SalticamGain = Field(..., title="Gain", description="Gain")
    readout_speed: SalticamReadoutSpeed = Field(
        ..., title="Readout speed", description="Readout speed"
    )
    detector_windows: Optional[List[SalticamDetectorWindow]] = Field(
        ..., title="Detector window", description="Detector window"
    )


class SalticamFilter(BaseModel):
    """Salticam filter."""

    name: str = Field(..., title="Name", description="Name of the filter")
    description: str = Field(
        ..., title="Description", description="Description of the filter"
    )


class SalticamExposure(BaseModel):
    """Salticam filter and exposure time."""

    filter: SalticamFilter = Field(..., title="Filter", description="Filter")
    exposure_time: float = Field(
        ..., title="Exposure time", description="Exposure time per exposure, in seconds"
    )


class SalticamProcedure(BaseModel):
    cycles: int = Field(
        ...,
        title="Cycles",
        description="Number of cycles, i.e. how often to execute the procedure",
    )
    exposures: List[SalticamExposure] = Field(
        ...,
        title="Exposures",
        description="Sequence of filters and exposure times to use",
    )


class Salticam(BaseModel):
    """Salticam setup."""

    id: int = Field(
        ..., title="Salticam id", description="Unique identifier for the Salticam setup"
    )
    detector: SalticamDetector = Field(
        ..., title="Detector setup", description="Detector setup"
    )
    procedure: SalticamProcedure = Field(
        ..., title="Instrument procedure", description="Instrument procedure"
    )
    minimum_signal_to_noise: int = Field(
        ...,
        title="Minimum signal-to-noise",
        description="Minimum signal-to-noise ratio required",
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


class SalticamSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["Salticam"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
    grating: Optional[str] = Field(..., title="Grating", description="Grating")
