from enum import Enum
from typing import NamedTuple


class User(NamedTuple):
    id: int
    username: str
    given_name: str
    family_name: str
    email: str
    password_hash: str


class Role(str, Enum):
    SALT_ASTRONOMER = "SALT Astronomer"
    ADMINISTRATOR = "Administrator"
    TAC_MEMBER = "TAC Member"
    TAC_CHAIR = "TAC Chair"
    BOARD_MEMBER = "Board Member"
