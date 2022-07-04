from typing import Any

from pydantic import BaseModel

Block = Any

BlockStatus = Any

BlockVisit = Any


class BlockVisitStatus(BaseModel):
    status: str
    rejection_reason: str
