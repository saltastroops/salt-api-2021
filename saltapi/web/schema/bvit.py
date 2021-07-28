from typing import List, Literal

from pydantic import BaseModel, Field


class BvitSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["BVIT"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
