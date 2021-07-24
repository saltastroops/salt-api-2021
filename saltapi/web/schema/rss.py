from enum import Enum
from typing import List, Literal

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
