from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class RssMode(str, Enum):
    """RSS modes."""

    FABRY_PEROT = "Fabry Perot"
    FP_POLARIMETRY = "FP polarimetry"
    IMAGING = "Imaging"
    MOS = "MOS"
    MOS_POLARIMETRY = "MOS polarimetry"
    POLARIMETRIC_IMAGING = "Polarimetric imaging"
    SPECTROPOLARIMETRY = "Spectropolarimetry"
    SPECTROSCOPY = "Spectroscopy"


class RssSummary(BaseModel):
    """Summary information for RSS."""

    name: Literal["RSS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[RssMode] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )


class RssGrating(str, Enum):
    """RSS grating."""

    OPEN = "Open"
    PG0300 = "pg0300"
    PG0900 = "pg0900"
    PG1300 = "pg1300"
    PG1800 = "pg1800"
    PG2300 = "pg2300"
    PG3000 = "pg3000"


class RssSpectroscopy(BaseModel):
    """RSS spectroscopy setup."""

    grating: RssGrating = Field(..., title="Grating", description="Grating")
    grating_angle: float = Field(
        ..., title="Grating angle", description="Grating angle, in degrees", ge=0
    )
    camera_angle: float = Field(
        ...,
        title="Camera angle",
        description="Camera (articulation) angle, in degrees",
        ge=0,
    )


class RssFabryPerotMode(str, Enum):
    """RSS Fabry-Pérot mode."""

    HR = ("High Resolution",)
    LR = ("Low Resolution",)
    MR = ("Medium Resolution",)
    TF = "Tunable Filter"


class RssFabryPerot(BaseModel):
    """RSS Fabry-Perot setup."""

    mode: RssFabryPerotMode = Field(
        ..., title="Fabry-Pérot mode", description="Fabry-Pérot mode (resolution)"
    )


class RssBeamSplitterOrientation(BaseModel):
    """RSS beam splitter orientation."""

    NORMAL = "Normal"
    PARALLEL = "Parallel"


class RssPolarimetry(BaseModel):
    """RSS polarimetry setup."""

    beam_splitter_orientation: RssBeamSplitterOrientation = Field(
        ...,
        title="Beam splitter orientation",
        description="Orientation of the beam splitter",
    )


class RssMaskType(str, Enum):
    """RSS mask type."""

    ENGINEERING = "Engineering"
    IMAGING = "Imaging"
    LONGSLIT = "Longslit"
    MOS = "MOS"
    POLARIMETRIC = "Polarimetric"


class RssMask(BaseModel):
    """RSS mask."""

    barcode: str = Field(
        ..., title="Barcode", description="Barcode identifying the mask"
    )
    mask_type: RssMaskType = Field(..., title="Mask type", description="Mask type")


class RssMosMask(RssMask):
    """RSS MOS mask."""

    equinox: Optional[float] = Field(
        ..., title="Equinox", description="Equinox of the mask coordinates"
    )
    cut_by: Optional[str] = Field(
        ..., title="Cut by", description="Person who cut the mask"
    )
    cut_date: Optional[str] = Field(
        ..., title="Cut date", description="Date when the mask was cut"
    )
    comment: Optional[str] = Field(
        ...,
        title="Comment",
        description="Comment regarding the production and handling of the mask",
    )


class RssConfiguration(BaseModel):
    """RSS instrument configuration."""

    mode: RssMode = Field(..., title="Instrument mode", description="Instrument mode")
    spectroscopy: Optional[RssSpectroscopy] = Field(
        ..., title="Spectroscopy setup", description="Spectroscopy setup"
    )
    fabry_perot: Optional[RssFabryPerot] = Field(
        ..., title="Fabry-Pérot setup", description="Fabry-Pérot setup"
    )
    polarimetry: Optional[RssPolarimetry] = Field(
        ..., title="Polarimetry setup", description="Polarimetry setup"
    )
    filter: str = Field(..., title="Filter", description="Filter")
    mask: Optional[Union[RssMask, RssMosMask]] = Field(
        ..., title="Slit mask", description="Slit mask"
    )


class RssDetectorMode(str, Enum):
    """RSS detector mode."""

    DRIFT_SCAN = "Drift Scan"
    FRAME_TRANSFER = "Frame Transfer"
    NORMAL = "Normal"
    SHUFFLE = "Shuffle"
    SLOT_MODE = "Slot Mode"


class RssExposureType(str, Enum):
    """RSS exposure type."""

    ARC = "Arc"
    BIAS = "Bias"
    DARK = "Dark"
    FLAT_FIELD = "Flat Field"
    SCIENCE = "Science"


class RssGain(str, Enum):
    """RSS gain."""

    BRIGHT = "Bright"
    FAINT = "Faint"


class RssReadoutSpeed(str, Enum):
    """RSS detector readout speed."""

    FAST = "Fast"
    NONE = "None"
    SLOW = "Slow"


class RssDetectorCalculation(str, Enum):
    """RSS detector calculation."""

    FOCUS = "Focus"
    FPRINGRADIUS = "FP Ring Radius"
    MOS_ACQUISITION = "MOS Acquisition"
    MOS_MASK_CALIB = "MOS Mask Calibration"
    MOS_SCAN = "MOS Scan"
    NOD_AND_SHUFFLE = "Nod & Shuffle"
    NONE = "None"


class RssDetectorWindow(BaseModel):
    """RSS detector window."""

    height: int = Field(
        ..., title="Height", description="Height of the window, in arcseconds", gt=0
    )


class RssDetector(BaseModel):
    """Rss detector setup."""

    mode: RssDetectorMode = Field(
        ..., title="Detector mode", description="Detector mode"
    )
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
        title="Pre-binned rows",
        description="Number of CCD rows to combine during readout",
        ge=1,
    )
    exposure_time: float = Field(
        ...,
        title="Exposure time",
        description="Exposure time per exposure, in seconds",
        ge=0,
    )
    iterations: int = Field(
        ..., title="Number of exposures", description="Number of exposures", ge=1
    )
    exposure_type: RssExposureType = Field(
        ..., title="Exposure type", description="Exposure type"
    )
    gain: RssGain = Field(..., title="Gain", description="Gain")
    readout_speed: RssReadoutSpeed = Field(
        ..., title="Readout speed", description="Readout speed"
    )
    detector_calculation: RssDetectorCalculation = Field(
        ..., title="Detector calculation", description="Detector calculation"
    )
    detector_window: Optional[RssDetectorWindow] = Field(
        ..., title="Detector window", description="Detector window"
    )


class RssProcedureType(str, Enum):
    """RSS procedure type."""

    FABRY_PEROT = "Fabry Perot"
    FOCUS = "Focus"
    FP_CAL = "FP Cal"
    FP_POLARIMETRY = "FP Polarimetry"
    FP_RING = "FP Ring"
    MOS_ACQUISITION = "MOS Acquisition"
    MOS_CALIBRATION = "MOS Calibration"
    MOS_PEAKUP = "MOS Peakup"
    NOD_AND_SHUFFLE = "Node and Shuffle"
    NORMAL = "Normal"
    POLARIMETRY = "Polarimetry"


class RssWaveplateAnglePair(BaseModel):
    """Half-wave plate and quarter-wave plate angle pair."""

    half_wave: Optional[float] = Field(
        ...,
        title="Half-wave plate angle",
        description="Angle of the half-wave plate, in degrees",
    )
    quarter_wave: Optional[float] = Field(
        ...,
        title="Quarter-wave plate angle",
        description="Angle of the quarter-wave plate, in degrees",
    )


class RssPolarimetryPattern(BaseModel):
    name: str = Field(..., title="Name", description="Name of the pattern")
    wave_plate_angles: List[RssWaveplateAnglePair] = Field(
        ...,
        title="Wave plate angles",
        description="Sequence of angles for the half-wave and quarter-wave plate",
    )


class RssProcedure(BaseModel):
    """RSS procedure."""

    procedure_type: RssProcedureType = Field(
        ..., title="Procedure type", description="Procedure type"
    )
    etalon_wavelengths: Optional[List[float]] = Field(
        ...,
        title="Etalon wavelengths",
        description="Sequence of Fabry-Pérot etalon wavelengths, in Ångstroms",
    )
    polarimetry_pattern: Optional[List[RssWaveplateAnglePair]] = Field(
        ...,
        title="Polarimetry pattern",
        description="Polarimetry pattern",
    )


class Rss(BaseModel):
    """Rss setup."""

    id: int = Field(
        ..., title="RSS id", description="Unique identifier for the RSS setup"
    )
    name: Literal["RSS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    cycles: int = Field(
        ...,
        title="Cycles",
        description="Number of cycles, i.e. how often to execute the procedure",
    )
    configuration: RssConfiguration = Field(
        ..., title="Instrument configuration", description="Instrument configuration"
    )
    detector: RssDetector = Field(
        ..., title="Detector setup", description="Detector setup"
    )
    procedure: RssProcedure = Field(
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
