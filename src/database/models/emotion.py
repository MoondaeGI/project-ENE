"""Emotion-related ORM models: CharacterState, EmotionHistory."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.memory import Message
    from database.models.participant import Participant


class CharacterState(Base):
    """AI 캐릭터의 현재 감정/상태 테이블."""

    __tablename__ = "character_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), unique=True, nullable=False
    )
    latest_emotion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("emotion_history.id"))
    energy_level: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    engagement_level: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    conversation_mode: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    character: Mapped[Participant] = relationship("Participant", back_populates="character_state")
    latest_emotion: Mapped[EmotionHistory | None] = relationship(
        "EmotionHistory", foreign_keys=[latest_emotion_id]
    )

    __table_args__ = (
        CheckConstraint("energy_level BETWEEN 0 AND 1", name="ck_character_state_energy"),
        CheckConstraint("engagement_level BETWEEN 0 AND 1", name="ck_character_state_engagement"),
    )


class EmotionHistory(Base):
    """메시지별 감정 기록 테이블."""

    __tablename__ = "emotion_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message.id")
    )
    joy: Mapped[float] = mapped_column(Float, nullable=False)
    sadness: Mapped[float] = mapped_column(Float, nullable=False)
    anger: Mapped[float] = mapped_column(Float, nullable=False)
    surprise: Mapped[float] = mapped_column(Float, nullable=False)
    fear: Mapped[float] = mapped_column(Float, nullable=False)
    disgust: Mapped[float] = mapped_column(Float, nullable=False)
    trigger_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    character: Mapped[Participant] = relationship("Participant", back_populates="emotion_histories")
    message: Mapped[Message | None] = relationship("Message", back_populates="emotion_histories")

    __table_args__ = (
        CheckConstraint("joy BETWEEN 0 AND 1", name="ck_emotion_joy"),
        CheckConstraint("sadness BETWEEN 0 AND 1", name="ck_emotion_sadness"),
        CheckConstraint("anger BETWEEN 0 AND 1", name="ck_emotion_anger"),
        CheckConstraint("surprise BETWEEN 0 AND 1", name="ck_emotion_surprise"),
        CheckConstraint("fear BETWEEN 0 AND 1", name="ck_emotion_fear"),
        CheckConstraint("disgust BETWEEN 0 AND 1", name="ck_emotion_disgust"),
        Index("emotion_history_character_idx", "character_id", "created_at"),
        Index("emotion_history_message_idx", "message_id"),
    )
