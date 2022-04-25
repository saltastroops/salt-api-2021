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
    primary_email: EmailStr
    email: List[str]


@dataclass()
class UserListItem:
    id: int
    family_name: str
    given_name: str


@dataclass()
class Affiliation:
    institution_id: int
    institution: str
    department: Optional[str]
    partner_code: str


@dataclass()
class User:
    id: int
    given_name: str
    family_name: str
    primary_email: EmailStr
    email: List[str]
    username: str
    password_hash: str
    affiliations: List[Affiliation]
    roles: List[Role]


@dataclass()
class NewUserDetails:
    given_name: str
    family_name: str
    primary_email: EmailStr
    email: List[str]
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
