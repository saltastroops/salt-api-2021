from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class SlitMask(BaseModel):
    proposal_id: int = Field(..., title="Proposal id", description="The proposal id")
    proposal_code: str = Field(..., title="Proposal code", description="The proposal code")
    proposal_code_id: int = Field(..., title="Proposal code id", description="The proposal code id")
    pi_surname: str = Field(..., title="Principal investigator's surname", description="The principal investigator's surname")
    block_status: str = Field(..., title="Block status", description="The block status")
    status: str = Field(..., title="Status", description="The status")
    block_name: str = Field(..., title="block name", description="The block name")
    priority: int = Field(..., title="Block priority", description="The block priority")
    n_visits: int = Field(..., title="Number of visits", description="The number of visits")
    n_done: int = Field(..., title="Number of completed visits", description="The number of completed visits")
    mask_id: int = Field(..., title="Mask id", description="The mask id")
    barcode: str = Field(..., title="Barcode", description="The slit mask barcode")
    ra_centre: float = Field(..., title="?", description="The ?")
    cut_by: Optional[str] = Field(..., title="Cut date", description="The slit mask cut date")
    cut_date: Optional[date] = Field(..., title="Cut date ", description="The slit mask cut date ")
    sa_comment: Optional[str] = Field(..., title="SALT astronomer comment", description="The SALT astronomer comment")


class MosData(BaseModel):
    """Mos Data."""

    mos_data: List[SlitMask] = Field(
        ..., title="Comment", description="Text of the comment")
    current_masks: List[str] = Field(
        ..., title="Comment", description="Text of the comment")
