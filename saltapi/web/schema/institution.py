from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from saltapi.web.schema.common import PartnerCode


class Institution(BaseModel):
    """An institute affiliation."""

    institution_id: int = Field(
        ...,
        title="Institute id",
        description="Unique identifier of the institute.",
    )
    partner_code: PartnerCode = Field(
        ...,
        title="SALT partner code",
        description="Code of the SALT Partner",
    )
    institution: str = Field(..., title="Institute", description="Institute")
    department: Optional[str] = Field(
        None, title="Department", description="Department of the institute"
    )
