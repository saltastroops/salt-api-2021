from typing import List, Optional

from pydantic import BaseModel, Field


class Institute(BaseModel):
    """Institute details"""

    institute_id: int = Field(
        ...,
        title="Institute id",
        description="Unique identifier of the institute to which the user is affiliated.",
    )
    name: str = Field(..., title="Institute name", description="Institute name")
    department: Optional[str] = Field(..., title="Department", description="Department")


class PartnerInstitutes(BaseModel):
    """User institute affiliation."""

    partners: str = Field(..., title="Partner", description="Partner")
    institutes: Institute = Field(
        ...,
        title="Institutes for the partner",
        description="Institutes for the partner",
    )


class Affiliation(BaseModel):
    """List of institutes affiliations."""

    partner: str = Field(
        ..., title="Partner institution", description="Partner institution"
    )
    institutes: List[str] = Field(..., title="Institutes", description="Institutes")
