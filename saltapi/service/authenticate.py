from datetime import date

from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str
    expires_at: date
