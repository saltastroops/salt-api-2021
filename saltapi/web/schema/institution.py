from typing import Optional

from pydantic import BaseModel, Field

from saltapi.web.schema.common import PartnerCode


class Institution(BaseModel):
    """An institution."""

    institution_id: int = Field(
        ...,
        title="Institution id",
        description="Unique identifier of the institution.",
    )
    partner_code: PartnerCode = Field(
        ...,
        title="SALT partner code",
        description="Code of the SALT Partner",
    )
    name: str = Field(..., title="Institution", description="Institution")
    department: Optional[str] = Field(
        None, title="Department", description="Department of the institution"
    )
