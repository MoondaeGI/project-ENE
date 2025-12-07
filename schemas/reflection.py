from typing import Optional
from datetime import datetime
from models.base import BaseModel


class ReflectionCreate(BaseModel):
    """Reflection 생성 스키마"""
    summary: str
    parent_id: Optional[int] = None


class ReflectionResponse(BaseModel):
    """Reflection 응답 스키마"""
    id: int
    parent_id: Optional[int]
    summary: str
    created_at: datetime

