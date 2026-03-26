"""SQLAlchemy ORM models for the AI Character Chat System.

Schema is aligned with database_schema.md.
Key design decisions:
- UUID: participant, message (external-facing)
- SERIAL: all internal tables
- memory_base: shared attributes for all memory objects
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ParticipantType(str, enum.Enum):
    HUMAN = "HUMAN"
    AI_CHARACTER = "AI_CHARACTER"


class EpisodeStatus(str, enum.Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"


# ---------------------------------------------------------------------------
# Participant
# ---------------------------------------------------------------------------


class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ParticipantType] = mapped_column(
        Enum(ParticipantType, name="participant_type"), nullable=False
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


# ---------------------------------------------------------------------------
# Memory Base
# ---------------------------------------------------------------------------


class MemoryBase(Base):
    __tablename__ = "memory_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    memory_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # message/observation/episode/reflection

    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    memory_strength: Mapped[float] = mapped_column(Float, nullable=False)
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    owner: Mapped[Participant] = relationship("Participant", back_populates="memory_bases")
    message: Mapped[Message | None] = relationship(
        "Message", back_populates="memory_base", uselist=False
    )
    observations: Mapped[list[Observation]] = relationship(
        "Observation", back_populates="memory_base"
    )
    episode: Mapped[Episode | None] = relationship(
        "Episode", back_populates="memory_base", uselist=False
    )
    reflection: Mapped[Reflection | None] = relationship(
        "Reflection", back_populates="memory_base", uselist=False
    )
    access_logs: Mapped[list[MemoryAccessLog]] = relationship(
        "MemoryAccessLog", back_populates="memory"
    )
    reflection_sources: Mapped[list[ReflectionSource]] = relationship(
        "ReflectionSource", back_populates="source_memory"
    )

    __table_args__ = (
        CheckConstraint("importance_score BETWEEN 0 AND 1", name="ck_memory_base_importance"),
        CheckConstraint("memory_strength BETWEEN 0 AND 1", name="ck_memory_base_strength"),
        Index("memory_base_owner_idx", "owner_id", "created_at"),
        Index("memory_base_type_idx", "memory_type"),
        Index("memory_base_strength_idx", "memory_strength"),
        Index("memory_base_owner_strength_idx", "owner_id", "memory_strength"),
        Index(
            "memory_base_embedding_idx",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class Message(Base):
    __tablename__ = "message"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_base.id"), unique=True, nullable=False
    )
    episode_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("episode.id"))
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    memory_base: Mapped[MemoryBase] = relationship("MemoryBase", back_populates="message")
    episode: Mapped[Episode | None] = relationship("Episode", back_populates="messages")
    sender: Mapped[Participant] = relationship("Participant", back_populates="messages")
    emotion_histories: Mapped[list[EmotionHistory]] = relationship(
        "EmotionHistory", back_populates="message"
    )

    __table_args__ = (
        Index("message_sender_idx", "sender_id", "created_at"),
        Index("message_memory_idx", "memory_id"),
        Index("message_episode_idx", "episode_id", "created_at"),
    )


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------


class Observation(Base):
    __tablename__ = "observation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_id: Mapped[int] = mapped_column(Integer, ForeignKey("memory_base.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    memory_base: Mapped[MemoryBase] = relationship("MemoryBase", back_populates="observations")

    __table_args__ = (Index("observation_memory_idx", "memory_id"),)


# ---------------------------------------------------------------------------
# Episode
# ---------------------------------------------------------------------------


class Episode(Base):
    __tablename__ = "episode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_base.id"), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text)
    turning_point: Mapped[str | None] = mapped_column(Text)
    conclusion: Mapped[str | None] = mapped_column(Text)
    status: Mapped[EpisodeStatus] = mapped_column(
        Enum(EpisodeStatus, name="episode_status"),
        default=EpisodeStatus.ONGOING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    memory_base: Mapped[MemoryBase] = relationship("MemoryBase", back_populates="episode")
    messages: Mapped[list[Message]] = relationship("Message", back_populates="episode")

    __table_args__ = (
        Index("episode_memory_idx", "memory_id"),
        Index("episode_status_idx", "status"),
    )


# ---------------------------------------------------------------------------
# Reflection
# ---------------------------------------------------------------------------


class Reflection(Base):
    __tablename__ = "reflection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_base.id"), unique=True, nullable=False
    )
    parent_reflection_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("reflection.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    memory_base: Mapped[MemoryBase] = relationship("MemoryBase", back_populates="reflection")
    parent: Mapped[Reflection | None] = relationship(
        "Reflection", remote_side="Reflection.id", back_populates="children"
    )
    children: Mapped[list[Reflection]] = relationship("Reflection", back_populates="parent")
    sources: Mapped[list[ReflectionSource]] = relationship(
        "ReflectionSource", back_populates="reflection"
    )

    __table_args__ = (
        Index("reflection_memory_idx", "memory_id"),
        Index("reflection_parent_idx", "parent_reflection_id"),
    )


class ReflectionSource(Base):
    __tablename__ = "reflection_source"

    reflection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reflection.id", ondelete="CASCADE"), primary_key=True
    )
    source_memory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_base.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    reflection: Mapped[Reflection] = relationship("Reflection", back_populates="sources")
    source_memory: Mapped[MemoryBase] = relationship(
        "MemoryBase", back_populates="reflection_sources"
    )

    __table_args__ = (
        Index("reflection_source_reflection_idx", "reflection_id"),
        Index("reflection_source_memory_idx", "source_memory_id"),
    )


# ---------------------------------------------------------------------------
# Memory Access Log
# ---------------------------------------------------------------------------


class MemoryAccessLog(Base):
    __tablename__ = "memory_access_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("memory_base.id", ondelete="CASCADE"), nullable=False
    )
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    access_context: Mapped[str | None] = mapped_column(Text)
    retrieval_score: Mapped[float | None] = mapped_column(Float)
    reinforcement_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    memory: Mapped[MemoryBase] = relationship("MemoryBase", back_populates="access_logs")

    __table_args__ = (Index("memory_access_log_memory_idx", "memory_id", "accessed_at"),)


# ---------------------------------------------------------------------------
# Character State & Emotion
# ---------------------------------------------------------------------------


class CharacterState(Base):
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


# ---------------------------------------------------------------------------
# User Understanding
# ---------------------------------------------------------------------------


class UserPortrait(Base):
    __tablename__ = "user_portrait"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), unique=True, nullable=False
    )
    personality_summary: Mapped[str | None] = mapped_column(Text)
    communication_style: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_portrait")
    traits: Mapped[list[UserTrait]] = relationship(
        "UserTrait", back_populates="portrait", cascade="all, delete-orphan"
    )
    state_snapshots: Mapped[list[UserStateSnapshot]] = relationship(
        "UserStateSnapshot", back_populates="user_portrait"
    )

    __table_args__ = (
        CheckConstraint("confidence_score BETWEEN 0 AND 1", name="ck_user_portrait_confidence"),
        Index("user_portrait_user_idx", "user_id"),
    )


class UserTrait(Base):
    __tablename__ = "user_trait"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portrait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_portrait.id", ondelete="CASCADE"), nullable=False
    )
    trait_name: Mapped[str] = mapped_column(Text, nullable=False)
    trait_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    portrait: Mapped[UserPortrait] = relationship("UserPortrait", back_populates="traits")
    snapshot_traits: Mapped[list[SnapshotTrait]] = relationship(
        "SnapshotTrait", back_populates="trait"
    )

    __table_args__ = (
        CheckConstraint("trait_value BETWEEN -1 AND 1", name="ck_user_trait_value"),
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_trait_confidence"),
        UniqueConstraint("portrait_id", "trait_name", name="uq_user_trait"),
        Index("user_trait_portrait_idx", "portrait_id"),
    )


class UserInterest(Base):
    __tablename__ = "user_interest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # -1(기피) ~ 1(관심)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    first_mentioned: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_mentioned: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_interests")
    snapshot_interests: Mapped[list[SnapshotInterest]] = relationship(
        "SnapshotInterest", back_populates="interest"
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_interest_confidence"),
        UniqueConstraint("user_id", "topic", name="uq_user_interest"),
        Index("user_interest_user_idx", "user_id", "confidence"),
        Index("user_interest_topic_idx", "topic"),
    )


class UserPreference(Base):
    __tablename__ = "user_preference"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    preference_type: Mapped[str] = mapped_column(Text, nullable=False)
    preference_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_preferences")
    snapshot_preferences: Mapped[list[SnapshotPreference]] = relationship(
        "SnapshotPreference", back_populates="preference"
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN -1 AND 1", name="ck_user_preference_confidence"),
        UniqueConstraint("user_id", "preference_type", name="uq_user_preference"),
        Index("user_preference_user_idx", "user_id"),
    )


# ---------------------------------------------------------------------------
# User State Snapshot
# ---------------------------------------------------------------------------


class UserStateSnapshot(Base):
    __tablename__ = "user_state_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    user_portrait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_portrait.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Participant] = relationship("Participant", back_populates="user_state_snapshots")
    user_portrait: Mapped[UserPortrait] = relationship(
        "UserPortrait", back_populates="state_snapshots"
    )
    snapshot_interests: Mapped[list[SnapshotInterest]] = relationship(
        "SnapshotInterest", back_populates="snapshot"
    )
    snapshot_traits: Mapped[list[SnapshotTrait]] = relationship(
        "SnapshotTrait", back_populates="snapshot"
    )
    snapshot_preferences: Mapped[list[SnapshotPreference]] = relationship(
        "SnapshotPreference", back_populates="snapshot"
    )

    __table_args__ = (Index("user_state_snapshot_user_idx", "user_id", "created_at"),)


class SnapshotInterest(Base):
    __tablename__ = "snapshot_interest"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    interest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_interest.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_interests"
    )
    interest: Mapped[UserInterest] = relationship(
        "UserInterest", back_populates="snapshot_interests"
    )

    __table_args__ = (Index("snapshot_interest_interest_idx", "interest_id"),)


class SnapshotTrait(Base):
    __tablename__ = "snapshot_trait"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    trait_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_trait.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_traits"
    )
    trait: Mapped[UserTrait] = relationship("UserTrait", back_populates="snapshot_traits")

    __table_args__ = (Index("snapshot_trait_trait_idx", "trait_id"),)


class SnapshotPreference(Base):
    __tablename__ = "snapshot_preference"

    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_state_snapshot.id", ondelete="CASCADE"), primary_key=True
    )
    preference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_preference.id", ondelete="CASCADE"), primary_key=True
    )

    snapshot: Mapped[UserStateSnapshot] = relationship(
        "UserStateSnapshot", back_populates="snapshot_preferences"
    )
    preference: Mapped[UserPreference] = relationship(
        "UserPreference", back_populates="snapshot_preferences"
    )

    __table_args__ = (Index("snapshot_preference_preference_idx", "preference_id"),)
