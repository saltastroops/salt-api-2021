from typing import NamedTuple, Optional


class User(NamedTuple):
    id: int
    username: str
    given_name: str
    family_name: str
    email: str
    password_hash: str


class UserToUpdate(NamedTuple):
    given_name: Optional[str]
    family_name: Optional[str]
    email: Optional[str]
    password: Optional[str]
