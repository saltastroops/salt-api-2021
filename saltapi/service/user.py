from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, NamedTuple, Optional


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
    email: str


@dataclass()
class UserListItem:
    id: int
    family_name: str
    given_name: str

    def asdict(self):  # type: ignore # noqa
        return asdict(self)


@dataclass()
class AffiliationListItem:
    partner: str
    institutes: List[str]

    def asdict(self):  # type: ignore # noqa
        return asdict(self)


@dataclass()
class Affiliation:
    partner: str
    institute: str


@dataclass()
class User:
    id: int
    username: str
    email: str
    given_name: str
    family_name: str
    password_hash: str
    affiliation: Affiliation
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
