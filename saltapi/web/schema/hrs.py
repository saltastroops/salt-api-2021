from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field


class HrsMode(str, Enum):
    """HRS modes."""

    HIGH_RESOLUTION = "High Resolution"
    HIGH_STABILITY = "High Stability"
    INT_CAL_FIBRE = "Int Cal Fibre"
    LOW_RESOLUTION = "Low Resolution"
    MEDIUM_RESOLUTION = "Medium Resolution"


class HrsSummary(BaseModel):
    """Summary information for RSS."""

    name: Literal["HRS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[HrsMode] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
