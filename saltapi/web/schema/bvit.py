from enum import Enum
from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Literal


class BvitFilter(str, Enum):
    """BVIT filter."""

    B = "B"
    H_ALPHA = "H-alpha"
    OPEN = "Open"
    R = "R"
    U = "U"
    V = "V"


class BvitMode(str, Enum):
    """BVIT instrument mode."""

    IMAGING = "Imaging"
    STREAMING = "Streaming"


class BvitNeutralDensity(str, Enum):
    """BVIT neutral density setting."""

    _0_3 = "0.3"
    _0_5 = "0.5"
    _1_0 = "1.0"
    _2_0 = "2.0"
    _3_0 = "3.0"
    _4_0 = "4.0"
    OPEN = "Open"


class Bvit(BaseModel):
    """BVIT setup."""

    id: int = Field(
        ..., title="BVIT id", description="Unique identifier for the BVIT setup"
    )
    mode: BvitMode = Field(..., title="Instrument mode", description="Instrument mode")
    filter: BvitFilter = Field(..., title="Filter", description="Filter")
    neutral_density: BvitNeutralDensity = Field(
        ..., title="Neutral density", description="Neutral density setting"
    )
    iris_size: float = Field(
        ..., title="Iris size", description="Iris size, in arcminutes"
    )
    shutter_open_time: float = Field(
        ...,
        title="Shutter open time",
        description="Time for which the shutter must remain open, in seconds",
    )


class BvitSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["BVIT"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
