from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    username_email: str = Field(
        ...,
        title="Username or email",
        description="Username or email address of the user whose password should be reset",
    )
