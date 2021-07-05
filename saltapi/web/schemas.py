import re
from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Generator, Callable, Dict, Any, Union, List, Optional

from pydantic import BaseModel, EmailStr,  Field, HttpUrl


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


class TextContent(BaseModel):
    """
    The text content of a proposal.

    Fields
    ------
    semester:
        Semester to which the text content belongs.
    title:
        Proposal title.
    abstract:
        Proposal abstract.
    read_me:
        Instructions for the observer.
    nightlog_summary:
        Brief (one-line) summary to include in the nightlog.
    """

    semester: Semester = Field(..., title="Semester", description="Semester to which the text content belongs")
    title: str = Field(..., title="Title", description="Proposal title")
    abstract: str = Field(..., title="Abstract", description="Proposal abstract")
    read_me: str = Field(..., title="Readme", description="Instructions for the observing SALT Astronomer")
    nightlog_summary: str = Field(..., title="Nightlog summmary", description="Brief (one-line) summary to include in the nightlog.")


class Partner(BaseModel):
    """A SALT partner."""
    code: str = Field(..., title="Partner code", description="Partner code, such as IUCAA or RSA")
    name: str = Field(..., title="Partner name", description="Partner name")


class Institute(BaseModel):
    """An institute."""
    partner: Partner = Field(..., title="SALT partner", description="SALT Partner to which the institute belongs")
    name: str = Field(..., title="Name", description="Institute name")
    department: Optional[str] = Field(None, title="Department", description="Department of the institute")
    home_page: HttpUrl = Field(..., title="Home page", description="URL of the institute's (or department's) home page")


class Investigator(BaseModel):
    """An investigator on a proposal."""
    is_pc: bool = Field(..., title="Principle Contact", description="Is this investigator the Principal Contact?")
    is_pi: bool = Field(..., title="Principle Investigator", description="Is this investigator the Principal Investigator?")
    given_name: str = Field(..., title="Given name", description="Given (\"first\") name")
    family_name: str = Field(..., title="Family name", description="Family (\"last\") name")
    email: EmailStr = Field(..., title="Email address", description="Email address")
    affiliation: Institute = Field(..., title="Affiliation", description="Institution to which the investigator is affiliated")


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


class TimeAllocation(BaseModel):
    """A time allocation."""
    semester: Semester = Field(..., title="Semester", description="Semester for which the time is allocated")
    partner: Partner = Field(..., title="SALT partner", description="SALT partner whose Time Allocation Committee is allocating the time")
    tac_comment: Optional[str] = Field(..., title="TAC comment", description="Comment by the Time Allocation Committee allocating the time")
    priority_0: Priority = Field(..., title="P0 time", description="Allocated priority 0 time, in seconds")
    priority_1: Priority = Field(..., title="P1 time", description="Allocated priority 1 time, in seconds")
    priority_2: Priority = Field(..., title="P2 time", description="Allocated priority 2 time, in seconds")
    priority_3: Priority = Field(..., title="P3 time", description="Allocated priority 3 time, in seconds")
    priority_4: Priority = Field(..., title="P4 time", description="Allocated priority 4 time, in seconds")


class ChargedTime(BaseModel):
    """Charged time, broken down by priority."""
    semester: Semester = Field(..., title="Semester", description="Semester for which the time is allocated")
    priority_0: Priority = Field(..., title="P0 time", description="Charged priority 0 time, in seconds")
    priority_1: Priority = Field(..., title="P1 time", description="Charged priority 1 time, in seconds")
    priority_2: Priority = Field(..., title="P2 time", description="Charged priority 2 time, in seconds")
    priority_3: Priority = Field(..., title="P3 time", description="Charged priority 3 time, in seconds")
    priority_4: Priority = Field(..., title="P4 time", description="Charged priority 4 time, in seconds")


class PartnerPercentage(BaseModel):
    """A percentage (for example of the requested time) for a partner."""
    partner: Partner = Field(..., title="SALT partner", description="SALT partner")
    percentage: float = Field(..., ge=0, le=100, title="Percentage", description="Percentage bewtween 0 and 100 (both inclusive)")


class Ranking(str, Enum):
    """A ranking (high, medium or low)."""
    HIGH = "High"
    LOW = "Low"
    MEDIUM = "Medium"


class BaseTarget(BaseModel):
    """Base model for targets."""
    id: int = Field(
        ..., title="Target id", description="Unique identifier of the target"
    )
    name: str = Field(..., title="Target name", description="Target name")


class Phase1Target(BaseTarget):
    """A target in a Phase 1 proposal."""
    right_ascension: float = Field(..., title="Right ascension", description="Right ascension, as an angle between 0 and 360 degrees (both inclusive)")
    declination: float = Field(..., title="Declination", description="Declination, as an angle between -90 and 90 degrees (both inclusive)")
    equinox: float = Field(..., title="Equinox", description="Equinox of the right ascension and declination")
    horizons_identifier: Optional[str] = Field(..., title="Horizons identifier", description="Identifier of the target in the Horizons database for solar system targets")
    minimum_magnitude: float = Field(..., title="Minimum magnitude", description="Minimum (brightest) magnitude")
    maximum_magnitude: float = Field(..., title="Maximum magnitude", description="Minimum (faintest) magnitude")
    target_type: str = Field(..., title="Target type", description="Target type (broad category)")
    target_subtype: str = Field(..., title="Target subtype", description="Target subtype")
    is_optional: bool = Field(..., title="Optional?", description="Whether the target is optional, i.e. whether it is part of a pool of targets from which only a subset needs to be observed.")
    n_visits: int = Field(..., title="Number of visits", description="Number of observations requested for the target")
    max_lunar_phase: float = Field(..., title="Maximum lunar phase", description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination")
    ranking: Ranking = Field(..., title="Ranking", description="Importance attributed by the Principal Investigator to observations of this target relative to other observations for the same proposal.")
    night_count: int = Field(..., title="Number of nights", description="Number of nights for which the target is observable, given the requested observation time and observation constraints.")
    # TODO: Comment on probabilities
    moon_probability: Optional[int]
    competition_probability: Optional[int]
    observability_probability: Optional[int]
    seeing_probability: Optional[int]


class RequestedTime(BaseModel):
    """Time requested in a phase 1 proposal."""
    total_requested_time: int = Field(..., title="Total requested time", description="Total requested time, in seconds")
    minimum_useful_time: Optional[int] = Field(..., title="Minimum useful time", description="Minimum time needed to produce meaningful science from the proposal, in seconds.")
    comment: Optional[str] = Field(None, title="Comment", description="Comment on the time requirements")
    semester: Semester = Field(..., title="Semester", description="Semester for which the time is requested")
    distribution: List[PartnerPercentage] = Field(..., title="Distribution among partners", description="Percentages of time requested from the different partners")


class ObservationStatus(str, Enum):
    """Observation status."""
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Observation(BaseModel):
    """An observation made."""
    id: int = Field(
        ..., title="Observation id", description="Unique identifier of the observation"
    )
    observation_time: int = Field(
        ...,
        title="observation time",
        description="Time charged for the observation, in seconds",
    )
    block_id: int = Field(
        ..., title="Block id", description="Unique identifier of the observed block"
    )
    priority: Priority = Field(
        ..., title="Priority", description="Priority of the observed block"
    )
    max_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, "
                    "as the percentage of lunar illumination",
    )
    targets: List[BaseTarget] = Field(
        ..., title="Observed targets", description="Observed targets"
    )
    observation_night: date = Field(
        ...,
        title="Observation night",
        description="Start date of the night when the observation was made",
    )
    status: ObservationStatus = Field(
        ...,
        title="Observation status",
        description="Status of the observation, "
                    "i.e. whether it has been accepted or rejected",
    )
    rejection_reason: Optional[str] = Field(
        None,
        title="Rejection reason",
        description="Reason why the observation has been rejected",
    )



class BaseProposal(BaseModel):
    """Base model for phase 1 and phase 2 proposals."""

    text_contents: List[TextContent] = Field(..., title="Text contents", description="Text contents for all semesters in the proposal")
    investigators: List[Investigator] = Field(..., title="Investigators", description="Investigators on the proposal")


class Phase1Proposal(BaseProposal):
    """A phase 1 proposal."""

    phase: int = Field(..., gt=0, lt=2, title="Proposal phase", description="Proposal phase, which must be 1")
    targets: List[Phase1Target] = Field(..., title="Targets", description="Targets for which observations are requested")
    requested_times: List[RequestedTime] = Field(..., title="Requested times", description="Requested times for all semesters in the proposal")


class Phase2Proposal(BaseProposal):
    """A phase 2 proposal."""

    phase: int = Field(..., gt=1, lt=3, title="Proposal phase", description="Proposal phase, which must be 1")
    observations: List[Observation] = Field(..., title="Observations", description="Observations made for the proposal in any semester")
    charged_times: List[ChargedTime] = Field(..., title="Charged times", description="Charged times for all semesters in the proposal")
    time_allocations: List[TimeAllocation] = Field(..., title="Time allocations", description="Time allocations for all semesters on the proposal")


class ProposalListItem(BaseModel):
    """Item in a list of proposals."""

    proposal_code: str = Field(..., title="Proposal code", description="Proposal code")

    class Config:
        schema_extra = {"example": {"proposal_code": "2021-1-SCI-074"}}


class SubmissionAcknowledgment(BaseModel):
    """Acknowledgment that a proposal submission has been received."""

    submission_id: int = Field(
        ...,
        title="Submission id",
        description="Unique identifier for a proposal submission",
    )

    class Config:
        schema_extra = {"example": {"submission_id": 41318}}


class ProposalContentType(str, Enum):
    """Content type for a proposal."""
    JSON = ("application/json",)
    PDF = ("application/pdf",)
    ZIP = "application/zip"


class ProposalStatus(str, Enum):
    """Proposal status."""
    ACCEPTED = "Accepted"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    DELETED = "Deleted"
    EXPIRED = "Expired"
    IN_PREPARATION = "In preparation"
    INACTIVE = "Inactive"
    REJECTED = "Rejected"
    SUPERSEDED = "Superseded"
    UNDER_SCIENTIFIC_REVIEW = "Under scientific review"
    UNDER_TECHNICAL_REVIEW = "Under technical review"


class ProposalStatusContent(BaseModel):
    """Content including a proposal status."""

    status: ProposalStatus = Field(
        ..., title="Proposal status", description="Proposal status"
    )


class ProposalContent(BaseModel):
    """
    Helper class.

    mypy does not like if a Union is used as the value of FastAPI's response_model in a
    path operation's decorator, so Union[Phase1Proposal, Phase2Proposal] cannot be used.
    This class can used instead.
    """

    __root__: Union[Phase1Proposal, Phase2Proposal]


class ObservationComment(BaseModel):
    """Comment related to an observation of a proposal."""

    author: str = Field(..., title="Author", description="Author of the comment")
    comment: str = Field(..., title="Comment", description="Text of the comment")
    madeAt: datetime = Field(
        ...,
        title="Time of creation",
        description="Date amd time when the comment was made",
    )

    class Config:
        schema_extra = {
            "example": {
                "author": "Sipho Mangana",
                "comment": "Please check the position angle.",
                "madeAt": "2019-08-24T14:15:22Z",
            }
        }


class ProgressReport(BaseModel):
    """
    Progress report for a proposal and semester. The semester is the semester for which
    the progress is reported. For example, if the semester is 2021-1, the report covers
    the observations up to and including the 2021-1 semester and it requests time for
    the 2021-2 semester.
    """

    dummy: str


class DataReleaseDate(BaseModel):
    """The release date when the observation data is scheduled to become public."""
    release_date: date = Field(
        ...,
        title="Data release date",
        description="Date when the proposal data is scheduled to become public",
    )


class DataReleaseDateUpdate(BaseModel):
    """A request to update the data release date."""
    release_date: date = Field(
        ...,
        title="Data release date",
        description="Requested date when the proposal data should become public",
    )
    motivation: date = Field(
        ...,
        title="Motivation",
        description="Motivation why the request should be granted",
    )
