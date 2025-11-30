"""사용자 스키마"""
from typing import Optional
from models.base import BaseModel


class UserCreate(BaseModel):
    """사용자 생성 스키마"""
    name: str
    email: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    """사용자 업데이트 스키마"""
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    id: int
    name: str
    email: str
    age: Optional[int] = None

