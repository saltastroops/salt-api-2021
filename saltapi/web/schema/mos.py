from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class MosBlock(BaseModel):
    """MOS data for a block."""

    proposal_code: str = Field(
        ..., title="Proposal code", description="The proposal code"
    )
    proposal_code_id: int = Field(
        ..., title="Proposal code id", description="The proposal code id"
    )
    pi_surname: str = Field(
        ...,
        title="Principal investigator's surname",
        description="The principal investigator's surname",
    )
    block_status: str = Field(..., title="Block status", description="The block status")
    block_name: str = Field(..., title="block name", description="The block name")
    priority: int = Field(..., title="Block priority", description="The block priority")
    n_visits: int = Field(
        ..., title="Number of visits", description="The number of visits"
    )
    n_done: int = Field(
        ...,
        title="Number of completed visits",
        description="The number of completed visits",
    )
    barcode: str = Field(..., title="Barcode", description="The slit mask barcode")
    ra_center: float = Field(
        ...,
        title="Right ascension of the mask centre",
        description="Right ascension of the mask centre, in degrees",
    )
    cut_by: Optional[str] = Field(
        ...,
        title="Cutting person",
        description="The name of the person who cut the slit mask",
    )
    cut_date: Optional[date] = Field(
        ..., title="Cut date ", description="The date when the slit mask was cut."
    )
    mask_comment: Optional[str] = Field(
        ..., title="Slit mask comment", description="A comment on the slit mask"
    )
    liaison_astronomer: Optional[str] = Field(
        ..., title="Liaison astronomer", description="The liaison astronomer"
    )
