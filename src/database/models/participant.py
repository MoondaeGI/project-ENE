"""Participant ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, ParticipantType

if TYPE_CHECKING:
    from database.models.emotion import CharacterState, EmotionHistory
    from database.models.memory import MemoryBase, Message
    from database.models.portrait import UserInterest, UserPortrait, UserPreference, UserStateSnapshot


class Participant(Base):
    """사용자 또는 AI 캐릭터를 나타내는 참여자 테이블."""

    __tablename__ = "participant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ParticipantType] = mapped_column(
        Enum(ParticipantType, name="participant_type", create_type=False), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    memory_bases: Mapped[list[MemoryBase]] = relationship("MemoryBase", back_populates="owner")
    messages: Mapped[list[Message]] = relationship("Message", back_populates="sender")
    character_state: Mapped[CharacterState | None] = relationship(
        "CharacterState", back_populates="character", uselist=False
    )
    emotion_histories: Mapped[list[EmotionHistory]] = relationship(
        "EmotionHistory", back_populates="character"
    )
    user_portrait: Mapped[UserPortrait | None] = relationship(
        "UserPortrait", back_populates="user", uselist=False
    )
    user_interests: Mapped[list[UserInterest]] = relationship("UserInterest", back_populates="user")
    user_preferences: Mapped[list[UserPreference]] = relationship(
        "UserPreference", back_populates="user"
    )
    user_state_snapshots: Mapped[list[UserStateSnapshot]] = relationship(
        "UserStateSnapshot", back_populates="user"
    )

    __table_args__ = (Index("participant_type_idx", "type"),)
