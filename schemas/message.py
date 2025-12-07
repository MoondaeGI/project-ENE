from typing import Optional
from datetime import datetime
from models.base import BaseModel
from models.message import MessageAction


class MessageCreate(BaseModel):
    person_id: int
    content: str
    action: MessageAction = MessageAction.PERSON


class PersonMessageCreate(BaseModel):
    person_id: int
    content: str


class AIMessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    person_id: Optional[int]
    content: str
    action: MessageAction
    created_at: datetime