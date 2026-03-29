"""Database ORM models package.

모든 모델을 여기서 import해야 SQLAlchemy mapper가 올바르게 등록됩니다.
외부에서는 `from database.models import Participant` 형태로 사용합니다.
"""

from database.models.base import Base, EpisodeStatus, ParticipantType
from database.models.emotion import CharacterState, EmotionHistory
from database.models.memory import (
    Episode,
    MemoryAccessLog,
    MemoryBase,
    Message,
    Observation,
    Reflection,
    ReflectionSource,
)
from database.models.participant import Participant
from database.models.portrait import (
    SnapshotInterest,
    SnapshotPreference,
    SnapshotTrait,
    UserInterest,
    UserPortrait,
    UserPreference,
    UserStateSnapshot,
    UserTrait,
)

__all__ = [
    "Base",
    "ParticipantType",
    "EpisodeStatus",
    "Participant",
    "MemoryBase",
    "Message",
    "Observation",
    "Episode",
    "Reflection",
    "ReflectionSource",
    "MemoryAccessLog",
    "CharacterState",
    "EmotionHistory",
    "UserPortrait",
    "UserTrait",
    "UserInterest",
    "UserPreference",
    "UserStateSnapshot",
    "SnapshotInterest",
    "SnapshotTrait",
    "SnapshotPreference",
]
