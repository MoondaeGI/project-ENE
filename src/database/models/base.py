"""SQLAlchemy declarative base and shared enums."""

from __future__ import annotations

import enum
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


class ParticipantType(str, enum.Enum):
    HUMAN = "HUMAN"
    AI_CHARACTER = "AI_CHARACTER"


class EpisodeStatus(str, enum.Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
