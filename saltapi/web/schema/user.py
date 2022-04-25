from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from saltapi.web.schema.common import Affiliation


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


class UserListItem(BaseModel):
    """Item in a list of users."""

    id: int = Field(..., title="User id", description="User id.")
    given_name: str = Field(..., title="Given name", description='Given ("first") name')
    family_name: str = Field(
        ..., title="Family name", description='Family ("last") name'
    )


class Usernames(BaseModel):
    given_name: str = Field(..., title="Given name", description='Given ("first") name')
    family_name: str = Field(
        ..., title="Family name", description='Family ("last") name'
    )

    class Config:
        orm_mode = True


class User(Usernames):
    """List of affiliations of the users."""

    id: int = Field(..., title="User id", description="User id.")
    primary_email: EmailStr = Field(
        ..., title="Email address", description="Email address"
    )
    email: List[str] = Field(
        ...,
        title="Alternative email addresses",
        description="Alternative email addresses",
    )
    username: str = Field(..., title="Username", description="Username.")
    roles: List[UserRole] = Field(..., title="User roles", description="User roles.")
    affiliations: List[Affiliation] = Field(
        ..., title="Affiliation", description="Affiliation of the user"
    )


class NewUserDetails(Usernames):
    """Details for creating a user."""

    primary_email: EmailStr = Field(
        ..., title="Email address", description="Email address"
    )
    username: str = Field(..., title="Username", description="Username.")
    password: str = Field(..., title="Password", description="Password.")
    institute_id: int = Field(
        ...,
        title="Institute id",
        description="Unique identifier of the institute to which the user is affiliated.",
    )


class UserUpdate(BaseModel):
    """
    New user details.

    A None value means that the existing value should be kept.
    """

    username: Optional[str] = Field(None, title="Username", description="Username.")
    # Not implemented yet
    # given_name: Optional[str]
    # family_name: Optional[str]
    # email: Optional[str]
    password: Optional[str] = Field(None, title="Password", description="Password.")


class PasswordResetRequest(BaseModel):
    """Username or email address for which a password reset is requested."""

    username_email: str = Field(
        ...,
        title="Username or email",
        description="Username or email address of the user whose password should be reset",
    )
