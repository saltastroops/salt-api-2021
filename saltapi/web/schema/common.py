import re
from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Any, Callable, Dict, Generator, List, Optional

from pydantic import BaseModel, Field


class BlockVisitStatusValue(str, Enum):
    """Block visit status."""

    # The SDB also contains a status "Deleted", but the API should ignore block visits
    # with this status.
    ACCEPTED = "Accepted"
    IN_QUEUE = "In queue"
    REJECTED = "Rejected"


class BlockRejectionReason(str, Enum):
    """Block rejection reason."""

    INSTRUMENT_TECHNICAL_PROBLEMS = "Instrument technical problems"
    OBSERVING_CONDITIONS_NOT_MET = "Observing conditions not met"
    PHASE_2_PROBLEMS = "Phase 2 problems"
    TELESCOPE_TECHNICAL_PROBLEMS = "Telescope technical problems"
    OTHER = "Other"


class BaseBlockVisit(BaseModel):
    """A block visit, without block details."""

    id: int = Field(
        ..., title="Block visit id", description="Unique identifier of the block visit"
    )
    night: date = Field(
        ...,
        title="Observation night",
        description="Start date of the night when the observation was made (or the block visit was queued).",
    )
    status: BlockVisitStatusValue = Field(
        ...,
        title="Block visit status",
        description="Status of the block visit",
    )
    rejection_reason: Optional[BlockRejectionReason] = Field(
        None,
        title="Rejection reason",
        description="Reason why the block visit has been rejected",
    )


class Priority(IntEnum):
    """
    A block priority.

    Priority 0 is the highest priority and should only be used for a target of
    opportunity. Priority 4 observations are only done if there are no other
    observations with another priority.
    """

    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4


class BlockVisit(BaseBlockVisit):
    """An observation made."""

    block_id: int = Field(
        ..., title="Block id", description="Unique identifier of the observed block"
    )
    block_name: str = Field(
        ..., title="Block name", description="Name of the observed block."
    )
    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time charged for the observation, in seconds",
    )
    priority: Priority = Field(
        ..., title="Block priority", description="Priority of the observed block"
    )
    targets: List[str] = Field(
        ...,
        title="Targets",
        description="List of the names of the observed targets. With the exception of a few legacy observations, the list contains a single target",
    )
    maximum_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination",
        ge=0,
        le=100,
    )


class Lamp(str, Enum):
    """Calibration lamp(s)."""

    AR = "Ar"
    AR_AND_THAR = "Ar and ThAr"
    CUAR = "CuAr"
    CUAR_AND_XE = "CuAr and Xe"
    HGAR = "HgAr"
    HGAR_AND_NE = "HgAr and Ne"
    NE = "Ne"
    QTH1 = "QTH1"
    QTH1_AND_QTH2 = "QTH1 and QTH2"
    QTH2 = "QTH2"
    THAR = "ThAr"
    XE = "Xe"


class ObservationProbabilities(BaseModel):
    """Probabilities related to observing."""

    moon: Optional[float] = Field(
        ...,
        title="Moon probability",
        description="Moon probability, which is derived from the lunar phase cumulative distribution function during the semester. The moon probability is not used in the total probability calculation since the moon constraints are already incorporated in the visibility window calculations",
    )
    competition: Optional[float] = Field(
        ...,
        title="Competition probability",
        description="Competition probability, which is determined as P_comp(x) = 1 / (C + 1) where C is the number of targets that overlap with target x",
        ge=0,
        le=1,
    )
    observability: Optional[float] = Field(
        ...,
        title="Observability probability",
        description="Probability representing the likelihood of pointing to a target given the length of its visibility window and the time requested on target. The probability is represented by the ratio of the length of the observing window and the length of the visibility window",
        ge=0,
        le=1,
    )
    seeing: Optional[float] = Field(
        ...,
        title="Seeing probability",
        description="Seeing probability, whivh is derived from the cumulative distribution function of seeing measurements taken in Sutherland",
        ge=0,
        le=1,
    )
    average_ranking: Optional[float] = Field(
        ..., title="Average ranking", description="Average ranking", ge=0
    )
    total: Optional[float] = Field(
        ...,
        title="Total probability",
        description="Total probability, which is derived using the binomial theorem, where the number of trials are the number of tracks available to observe a target, the number of successes is the number of visits requested and the probability per trial is the total probability per track",
        ge=0,
        le=1,
    )


class PartnerCode(str, Enum):
    """The partner codes of the past and current SALT partners."""

    AMNH = "AMNH"
    CMU = "CMU"
    DC = "DC"
    DUR = "DUR"
    GU = "GU"
    HET = "HET"
    IUCAA = "IUCAA"
    ORP = "ORP"
    OTH = "OTH"
    POL = "POL"
    RSA = "RSA"
    RU = "RU"
    UC = "UC"
    UKSC = "UKSC"
    UNC = "UNC"
    UW = "UW"


class PartnerName(str, Enum):
    """The past and current SALT partners."""

    AMNH = "American Museum of Natural History"
    CMU = "Carnegie Mellon University"
    DC = "Dartmouth College"
    DUR = "Durham University"
    GU = "Georg-August-Universität Göttingen"
    HET = "Hobby Eberly Telescope Board"
    IUCAA = "Inter-University Centre for Astronomy & Astrophysics"
    ORP = "OPTICON-Radionet Pilot"
    OTH = "Other"
    POL = "Poland"
    RSA = "South Africa"
    RU = "Rutgers University"
    UC = "University of Canterbury"
    UKSC = "UK SALT Consortium"
    UNC = "University of North Carolina - Chapel Hill"
    UW = "University of Wisconsin-Madison"


class ProposalCode(str):
    """
    A string denoting a semester, such as "2021-2-SCI-017".

    The string must consist of a four-digit year (between 2000 and 2099) followed by a
    dash, the semester ("1" or "2"), another dash, a combination of uppercase letters
    and underscores (which must start and end with a letter), another dash and three
    digits.
    """

    # Based on https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
    proposal_code_regex = r"20\d{2}-[12]-[A-Z][A-Z_]*[A-Z]-\d{3}"

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[str], str], None, None]:
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[Any, Any]) -> None:
        field_schema.update(
            pattern=ProposalCode.proposal_code_regex, examples=["2021-2-SCI-017"]
        )

    @classmethod
    def validate(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")
        m = re.match(Semester.semester_regex, v)
        if not m:
            raise ValueError("incorrect proposal code format")
        return v


class Ranking(str, Enum):
    """A ranking (high, medium or low)."""

    HIGH = "High"
    LOW = "Low"
    MEDIUM = "Medium"


class Semester(str):
    """
    A string denoting a semester, such as "2021-2" or "2022-1".

    The string must consist of a four-digit year (between 2000 and 2099) followed by a
    dash and "1" or "2".
    """

    # Based on https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
    semester_regex = r"20\d{2}-[12]"

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[str], str], None, None]:
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[Any, Any]) -> None:
        field_schema.update(
            pattern=Semester.semester_regex, examples=["2021-2", "2022-1"]
        )

    @classmethod
    def validate(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")
        m = re.match(Semester.semester_regex, v)
        if not m:
            raise ValueError("incorrect semester format")
        return v


class TargetCoordinates(BaseModel):
    """Target coordinates."""

    right_ascension: float = Field(
        ...,
        title="Right ascension",
        description="Right ascension, in degrees",
        ge=0,
        le=360,
    )
    declination: float = Field(
        ..., tile="Declination", description="Declination, in degrees", ge=-90, le=90
    )
    equinox: float = Field(..., title="Equinox", description="Equinox", ge=0)


class TimeInterval(BaseModel):
    """Observing window."""

    start: datetime = Field(
        ...,
        title="Interval start",
        description="Start time of the interval, in UTC",
    )
    end: datetime = Field(
        ..., title="Interval end", description="End time of the interval, in UTC"
    )


class Message(BaseModel):
    message: str = Field(..., title="Message", description="Message")


class Transparency(str, Enum):
    ANY = "Any"
    CLEAR = "Clear"
    THICK_CLOUD = "Thick cloud"
    THIN_CLOUD = "Thin cloud"
