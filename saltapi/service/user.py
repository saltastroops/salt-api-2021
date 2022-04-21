from dataclasses import dataclass
from enum import Enum
from typing import List, NamedTuple, Optional

from pydantic import EmailStr


class Role(str, Enum):
    SALT_ASTRONOMER = "SALT Astronomer"
    ADMINISTRATOR = "Administrator"
    TAC_MEMBER = "TAC Member"
    TAC_CHAIR = "TAC Chair"
    BOARD_MEMBER = "Board Member"


@dataclass()
class ContactDetails:
    given_name: str
    family_name: str
    emails: List[EmailStr]


@dataclass()
class UserListItem:
    id: int
    family_name: str
    given_name: str


@dataclass()
class Institute:
    institute_id: int
    name: str
    department: Optional[str]


@dataclass()
class PartnerInstitutes(Institute):
    partner_code: str


@dataclass()
class User:
    id: int
    username: str
    emails: List[str]
    given_name: str
    family_name: str
    password_hash: str
    affiliations: List[PartnerInstitutes]
    roles: List[Role]


@dataclass()
class NewUserDetails(ContactDetails):
    username: str
    password: str
    institute_id: int


class UserUpdate(NamedTuple):
    username: Optional[str]
    # Not implemented yet
    # given_name: Optional[str]
    # family_name: Optional[str]
    # email: Optional[str]
    password: Optional[str]
