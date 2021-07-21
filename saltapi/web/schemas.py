import re
from datetime import date, datetime
from enum import Enum, IntEnum
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Union,
)

from pydantic import BaseModel, EmailStr, Field


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


class PartnerName(str, Enum):
    """The past and current SALT partners."""

    AMNH = "American Museum of Natural History"
    CMU = "Carnegie Mellon University"
    DC = "Dartmouth College"
    DUR = "Durham University"
    GU = "Georg-August-Universität Göttingen"
    HET = "Hobby Eberly Telescope Board"
    IUCAA = "Inter-University Centre for Astronomy & Astrophysics"
    OTH = "Other"
    POL = "Poland"
    RSA = "South Africa"
    RU = "Rutgers University"
    UC = "University of Canterbury"
    UKSC = "UK SALT Consortium"
    UNC = "University of North Carolina - Chapel Hill"
    UW = "University of Wisconsin-Madison"


class PartnerCode(str, Enum):
    """The partner codes of the past and current SALT partners."""

    AMNH = "AMNH"
    CMU = "CMU"
    DC = "DC"
    DUR = "DUR"
    GU = "GU"
    HET = "HET"
    IUCAA = "IUCAA"
    OTH = "OTH"
    POL = "POL"
    RSA = "RSA"
    RU = "RU"
    UC = "UC"
    UKSC = "UKSC"
    UNC = "UNC"
    UW = "UW"


class Transparency(str, Enum):
    """Sky transparency."""

    ANY = "Any"
    CLEAR = "Clear"
    THICK_CLOUD = "Thick cloud"
    THIN_CLOUD = "Thin cloud"


class ContactDetails(BaseModel):
    given_name: str = Field(..., title="Given name", description='Given ("first") name')
    family_name: str = Field(
        ..., title="Family name", description='Family ("last") name'
    )
    email: EmailStr = Field(..., title="Email address", description="Email address")

    class Config:
        orm_mode = True


class Affiliation(BaseModel):
    """An institute affiliation."""

    partner_name: PartnerName = Field(
        ...,
        title="SALT partner name",
        description="Name of the SALT Partner",
    )
    partner_code: PartnerCode = Field(
        ...,
        title="SALT partner code",
        description="Code of the SALT Partner",
    )
    institute: str = Field(..., title="Institute", description="Institute")
    department: Optional[str] = Field(
        None, title="Department", description="Department of the institute"
    )


class Investigator(ContactDetails):
    """An investigator on a proposal."""

    user_id: int = Field(
        ..., title="User id", description="User id of the investigator"
    )
    affiliation: Affiliation = Field(
        ..., title="Affiliation", description="Affiliation of the investigator"
    )
    is_pc: bool = Field(
        ...,
        title="Principle Contact",
        description="Is this investigator the Principal Contact?",
    )
    is_pi: bool = Field(
        ...,
        title="Principle Investigator",
        description="Is this investigator the Principal Investigator?",
    )
    has_approved_proposal: Optional[bool] = Field(
        ...,
        title="Has approved proposal?",
        description="Whether the investigator has approved the proposal. The value is null if the investigator has neither approved nor rejected the proposal yet",
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


class TimeAllocation(BaseModel):
    """A time allocation."""

    partner_name: PartnerName = Field(
        ...,
        title="SALT partner name",
        description="Name of the SALT partner whose Time Allocation Committee is allocating the time",
    )
    partner_code: PartnerCode = Field(
        ...,
        title="SALT partner code",
        description="Code of the SALT partner whose Time Allocation Committee is allocating the time",
    )
    tac_comment: Optional[str] = Field(
        ...,
        title="TAC comment",
        description="Comment by the Time Allocation Committee allocating the time",
    )
    priority_0: int = Field(
        ..., title="P0 time", description="Allocated priority 0 time, in seconds", ge=0
    )
    priority_1: Priority = Field(
        ..., title="P1 time", description="Allocated priority 1 time, in seconds", ge=0
    )
    priority_2: Priority = Field(
        ..., title="P2 time", description="Allocated priority 2 time, in seconds", ge=0
    )
    priority_3: Priority = Field(
        ..., title="P3 time", description="Allocated priority 3 time, in seconds", ge=0
    )
    priority_4: Priority = Field(
        ..., title="P4 time", description="Allocated priority 4 time, in seconds", ge=0
    )


class ChargedTime(BaseModel):
    """Charged time, broken down by priority."""

    priority_0: int = Field(
        ..., title="P0 time", description="Charged priority 0 time, in seconds", ge=0
    )
    priority_1: int = Field(
        ..., title="P1 time", description="Charged priority 1 time, in seconds", ge=0
    )
    priority_2: int = Field(
        ..., title="P2 time", description="Charged priority 2 time, in seconds", ge=0
    )
    priority_3: int = Field(
        ..., title="P3 time", description="Charged priority 3 time, in seconds", ge=0
    )
    priority_4: int = Field(
        ..., title="P4 time", description="Charged priority 4 time, in seconds", ge=0
    )


class PartnerPercentage(BaseModel):
    """A percentage (for example of the requested time) for a partner."""

    partner: PartnerName = Field(..., title="SALT partner", description="SALT partner")
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        title="Percentage",
        description="Percentage bewtween 0 and 100 (both inclusive)",
    )


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

    right_ascension: float = Field(
        ...,
        title="Right ascension",
        description="Right ascension, as an angle between 0 and 360 degrees (both inclusive)",
    )
    declination: float = Field(
        ...,
        title="Declination",
        description="Declination, as an angle between -90 and 90 degrees (both inclusive)",
    )
    equinox: float = Field(
        ...,
        title="Equinox",
        description="Equinox of the right ascension and declination",
    )
    horizons_identifier: Optional[str] = Field(
        ...,
        title="Horizons identifier",
        description="Identifier of the target in the Horizons database for solar system targets",
    )
    minimum_magnitude: float = Field(
        ..., title="Minimum magnitude", description="Minimum (brightest) magnitude"
    )
    maximum_magnitude: float = Field(
        ..., title="Maximum magnitude", description="Minimum (faintest) magnitude"
    )
    target_type: str = Field(
        ..., title="Target type", description="Target type (broad category)"
    )
    target_subtype: str = Field(
        ..., title="Target subtype", description="Target subtype"
    )
    is_optional: bool = Field(
        ...,
        title="Optional?",
        description="Whether the target is optional, i.e. whether it is part of a pool of targets from which only a subset needs to be observed.",
    )
    n_visits: int = Field(
        ...,
        title="Number of visits",
        description="Number of observations requested for the target",
    )
    max_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination",
        ge=0,
        le=100,
    )
    ranking: Ranking = Field(
        ...,
        title="Ranking",
        description="Importance attributed by the Principal Investigator to observations of this target relative to other observations for the same proposal.",
    )
    night_count: int = Field(
        ...,
        title="Number of nights",
        description="Number of nights for which the target is observable, given the requested observation time and observation constraints.",
    )
    # TODO: Comment on probabilities
    moon_probability: Optional[float]
    competition_probability: Optional[float]
    observability_probability: Optional[float]
    seeing_probability: Optional[float]
    average_ranking: Optional[float]
    total_probability: Optional[float]


class RequestedTime(BaseModel):
    """Time requested in a phase 1 proposal."""

    total_requested_time: int = Field(
        ...,
        title="Total requested time",
        description="Total requested time, in seconds",
    )
    minimum_useful_time: Optional[int] = Field(
        ...,
        title="Minimum useful time",
        description="Minimum time needed to produce meaningful science from the proposal, in seconds.",
    )
    comment: Optional[str] = Field(
        None, title="Comment", description="Comment on the time requirements"
    )
    semester: Semester = Field(
        ..., title="Semester", description="Semester for which the time is requested"
    )
    distribution: List[PartnerPercentage] = Field(
        ...,
        title="Distribution among partners",
        description="Percentages of time requested from the different partners",
    )


class ObservationStatus(str, Enum):
    """Observation status."""

    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class ExecutedObservation(BaseModel):
    """An observation made."""

    id: int = Field(
        ..., title="Observation id", description="Unique identifier of the observation"
    )
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
    night: date = Field(
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


class ProposalType(str, Enum):
    """Proposal type."""

    COMMISSIONING = "Commissioning"
    DIRECTOR_DISCRETIONARY_TIME = "Director’s Discretionary Time"
    ENGINEERING = "Engineering"
    GRAVITATIONAL_WAVE_EVENT = "Gravitational Wave Event"
    KEY_SCIENCE_PROGRAM = "Key Science Program"
    LARGE_SCIENCE_PROPOSAL = "Large Science Proposal"
    SCIENCE = "Science"
    SCIENCE_LONG_TERM = "Science - Long Term"
    SCIENCE_VERIFICATION = "Science Verification"


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


class SalticamSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["Salticam"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )


class RssMode(str, Enum):
    """RSS modes."""

    FABRY_PEROT = "Fabry Perot"
    FP_POLARIMETRY = "FP polarimetry"
    IMAGING = "Imaging"
    MOS = "MOS"
    MOS_POLARIMETRY = "MOS polarimetry"
    POLARIMETRIC_IMAGING = "Polarimetric imaging"
    SPECTROPOLARIMETRY = "Spectropolarimetry"
    SPECTROSCOPY = "Spectroscopy"


class RssSummary(BaseModel):
    """Summary information for RSS."""

    name: Literal["RSS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[RssMode] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )


class HrsMode(str, Enum):
    """HRS modes."""

    HIGH_RESOLUTION = "High Resolution"
    HIGH_STABILITY = "High Stability"
    INT_CAL_FIBRE = "Int Cal Fibre"
    LOW_RESOLUTION = "Low Resolution"
    MEDIUM_RESOLUTION = "Medium Resolution"


class HrsSummary(BaseModel):
    """Summary information for RSS."""

    name: Literal["HRS"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[HrsMode] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )


class BvitSummary(BaseModel):
    """Summary information for Salticam."""

    name: Literal["BVIT"] = Field(
        ..., title="Instrument name", description="Instrument name"
    )
    modes: List[Literal[""]] = Field(
        ..., title="Instrument modes", description="Used instrument modes"
    )


class GeneralProposalInfo(BaseModel):
    """General proposal information for a semester."""

    title: str = Field(..., title="Title", description="Proposal title")
    abstract: str = Field(..., title="Abstract", description="Proposal abstract")
    current_submission: datetime = Field(
        ...,
        title="Current submission datetime",
        description="Datetime of the latest submission for any semester",
    )
    first_submission: datetime = Field(
        ...,
        title="First submission datetime",
        description="Datetime of the first submission for any semester",
    )
    submission_number: int = Field(
        ...,
        title="Submission number",
        description="Current submission number for any semester",
    )
    semesters: List[Semester] = Field(
        ...,
        title="Semesters",
        description="List of semesters for which the proposal has been submitted",
    )
    status: ProposalStatus = Field(
        ..., title="Proposal status", description="Proposal status"
    )
    proposal_type: ProposalType = Field(
        ..., title="Proposal type", description="Proposal type"
    )
    target_of_opportunity: bool = Field(
        ...,
        title="Target of opportunity?",
        description="Whether thec proposal contains targets of opportunity",
    )
    total_requested_time: int = Field(
        ...,
        title="Total requested time",
        description="Total requested time, in seconds",
    )
    data_release_date: date = Field(
        ...,
        title="Data release date",
        description="Date when the proposal data is scheduled to become public",
    )
    liaison_salt_astronomer: str = Field(
        ...,
        title="Liaison astronomer",
        description="SALT Astronomer who is the liaison astronomer for the proposal",
    )
    summary_for_salt_astronomer: str = Field(
        ...,
        title="Summary for the SALT Astronomer",
        description="Brief summary with the essential information for the SALT Astronomer",
    )
    summary_for_night_log: str = Field(
        ...,
        title="Summary for the night log",
        description="Brief (one-line) summary to include in the observing night log",
    )


class BlockSummary(BaseModel):
    """Summary information about a block."""

    id: int = Field(
        ..., title="Block id", description="Unique identifier for the block"
    )
    name: str = Field(..., title="Name", description="Block name")
    observation_time: int = Field(
        ...,
        title="Observation time",
        description="Time required to make an observation of the block, in seconds",
        ge=0,
    )
    priority: Priority = Field(
        ..., title="Priority", description="Priority of the block"
    )
    requested_observations: int = Field(
        ...,
        title="Requested observations",
        description="Number of observations requested for the block",
    )
    accepted_observations: int = Field(
        ...,
        title="Accepted observations",
        description="Number of accepted observations made for the block so far",
    )
    rejected_observations: int = Field(
        ...,
        title="Rejected observations",
        description="Number of rejected observations made for the block so far",
    )
    is_observable_tonight: bool = Field(
        ...,
        title="Observable tonight?",
        description="Whether the block can be observed tonight (i.e. during the current Julian day)",
    )
    remaining_nights: int = Field(
        ...,
        title="Remaining nights",
        description="Number of nights (Julian days), excluding the current one, during which the block still can be observed",
    )
    maximum_seeing: float = Field(
        ...,
        title="Maximum seeing",
        description="Maximum seeing allowed for an observation, in arcseconds",
        ge=0,
    )
    transparency: Transparency = Field(
        ...,
        title="Transparency",
        description="Sky transparency required for an observation",
    )
    maximum_lunar_phase: float = Field(
        ...,
        title="Maximum lunar phase",
        description="Maximum lunar phase which was allowed for the observation, as the percentage of lunar illumination",
        ge=0,
        le=100,
    )
    instruments: List[
        Union[SalticamSummary, RssSummary, HrsSummary, BvitSummary]
    ] = Field(..., title="Instruments", description="Instruments used for the block")


class BaseProposal(BaseModel):
    """Base model for phase 1 and phase 2 proposals."""

    proposal_code: ProposalCode = Field(
        ..., title="Proposal code", description="Proposal code"
    )
    semester: Semester = Field(
        ...,
        title="Semester",
        description="Semester for which the proposal details are given",
    )
    general_info: GeneralProposalInfo = Field(
        ...,
        title="General information",
        description="General proposal information for a semester",
    )
    investigators: List[Investigator] = Field(
        ..., title="Investigators", description="Investigators on the proposal"
    )


class Phase1Proposal(BaseProposal):
    """A phase 1 proposal."""

    phase: int = Field(
        ...,
        gt=0,
        lt=2,
        title="Proposal phase",
        description="Proposal phase, which must be 1",
    )
    targets: List[Phase1Target] = Field(
        ..., title="Targets", description="Targets for which observations are requested"
    )
    requested_times: List[RequestedTime] = Field(
        ...,
        title="Requested times",
        description="Requested times for all semesters in the proposal",
    )


class Phase2Proposal(BaseProposal):
    """A phase 2 proposal."""

    phase: int = Field(
        ...,
        gt=1,
        lt=3,
        title="Proposal phase",
        description="Proposal phase, which must be 2",
    )
    blocks: List[BlockSummary] = Field(
        ..., title="Blocks", description="Blocks for the semester"
    )
    executed_observations: List[ExecutedObservation] = Field(
        ...,
        title="Observations",
        description="Observations made for the proposal in any semester",
    )
    charged_time: ChargedTime = Field(
        ...,
        title="Charged time, by priority",
        description="Charged time, by priority, for the semester",
    )
    time_allocations: List[TimeAllocation] = Field(
        ...,
        title="Time allocations",
        description="Time allocations for the semester",
    )


class ProposalListItem(BaseModel):
    """Item in a list of proposals."""

    id: int = Field(
        ..., title="Proposal id", description="Unique identifier of the proposal"
    )
    proposal_code: str = Field(..., title="Proposal code", description="Proposal code")
    semester: Semester = Field(
        ...,
        title="Semester",
        description="Semester for which the proposal was submitted",
    )
    title: str = Field(..., title="Title", description="Proposal title")
    phase: int = Field(
        ..., gt=0, lt=3, title="Proposal phase", description="Proposal phase"
    )
    status: ProposalStatus = Field(
        ..., title="Proposal status", description="Proposal status"
    )
    proposal_type: ProposalType = Field(
        ..., title="Proposal type", description="Proposal type"
    )
    principal_investigator: ContactDetails = Field(
        ..., title="Principal Investigator", description="Principal Investigator"
    )
    principal_contact: ContactDetails = Field(
        ..., title="Principal Contact", description="Principal Contact"
    )
    liaison_astronomer: ContactDetails = Field(
        ..., title="Liaison Astronomer", description="Liaison Astronomer"
    )

    class Config:
        schema_extra = {"example": {"proposal_code": "2021-1-SCI-074"}}
        orm_mode = True


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


class InstrumentSummary(BaseModel):
    """Summary details of an instrument setup."""

    name: str = Field(..., title="Name", description="Instrument name")
    mode: str = Field(
        ...,
        title="Mode",
        description="Instrument mode. For Salticam this is just an empty string.",
    )
