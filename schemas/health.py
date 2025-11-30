"""헬스 체크 스키마"""
from models.base import BaseModel


class HealthResponse(BaseModel):
    """헬스 체크 응답 스키마"""
    status: str
    message: str

