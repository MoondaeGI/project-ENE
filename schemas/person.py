from typing import Optional
from models.base import BaseModel
from datetime import datetime


class PersonCreate(BaseModel):
    name: str


class PersonUpdate(BaseModel):
    name: Optional[str] = None


class PersonResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
