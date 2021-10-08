from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from saltapi.web.schema.proposal import ContactDetails


class UserRole(str, Enum):
    """
    User roles.

    In case of TAC members and chairs the role means that the user is a TAC member or
    chair for any (but not all) of the SALT partners.

    The administrator role refers to being an administrator for the API.
    """

    SALT_ASTRONOMER = "SALT Astronomer"
    ADMINISTRATOR = "Administrator"
    TAC_MEMBER = "TAC Member"
    TAC_CHAIR = "TAC Chair"
    BOARD_MEMBER = "Board Member"


class User(ContactDetails):
    """User details, including username, contact details and roles."""

    username: str = Field(..., title="Username", description="Username.")
    roles: List[UserRole] = Field(..., title="User roles", description="User roles.")


class PasswordResetRequest(BaseModel):
    """Username or email address for which a password reset is requested."""

    username_email: str = Field(
        ...,
        title="Username or email",
        description="Username or email address of the user whose password should be reset",
    )
