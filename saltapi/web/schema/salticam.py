from typing import List, Literal

from pydantic import BaseModel, Field


class SalticamSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["Salticam"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )
