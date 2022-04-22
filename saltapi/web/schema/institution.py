from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Partner(str, Enum):
    """SALT partner institutions"""

    GU = "Georg-August-Universität Göttingen"
    UW = "University of Wisconsin-Madison"
    RSA = "South Africa"
    OTH = "Other"
    UNC = "University of North Carolina - Chapel Hill"
    UKSC = "UK SALT Consortium"
    DC = "Dartmouth College"
    RU = "Rutgers University"
    POL = "Poland"
    CMU = "Carnegie Mellon University"
    UC = "University of Canterbury"
    HET = "Hobby Eberly Telescope Board"
    AMNH = "American Museum of Natural History"
    IUCAA = "Inter-University Centre for Astronomy & Astrophysics"
    DUR = "Durham University"


class PartnerInstitutes(BaseModel):
    """Institute details"""

    institute_id: int = Field(
        ...,
        title="Institute id",
        description="Unique identifier of the institute.",
    )
    name: str = Field(..., title="Institute name", description="Institute name")
    department: Optional[str] = Field(
        None, title="Department", description="Department"
    )
    partner_code: str = Field(..., title="Partner code", description="Partner code")
