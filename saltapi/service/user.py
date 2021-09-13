from typing import NamedTuple, Optional


class User(NamedTuple):
    id: int
    username: str
    given_name: str
    family_name: str
    email: str
    password_hash: str
