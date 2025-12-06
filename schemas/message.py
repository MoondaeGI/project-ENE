from typing import Optional
from datetime import datetime
from models.base import BaseModel


class MessageCreate(BaseModel):
    person_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    person_id: int
    content: str
    created_at: datetime