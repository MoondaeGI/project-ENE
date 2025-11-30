"""베이스 모델"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseModel(PydanticBaseModel):
    """베이스 모델 클래스"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


class TimestampMixin(BaseModel):
    """타임스탬프 믹스인"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

