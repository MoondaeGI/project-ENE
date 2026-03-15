"""SQLAlchemy ORM models for the AI Character Chat System.

All memory objects include: importance_score, access_count, created_at,
last_access_time, and embedding (VECTOR(1536) via pgvector).
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Shared declarative base."""
    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[str]: JSONB,
    }


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ActionType(str, enum.Enum):
    AI = "AI"
    PERSON = "PERSON"


class EpisodeStatus(str, enum.Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"


# ---------------------------------------------------------------------------
# Person
# ---------------------------------------------------------------------------

class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    messages: Mapped[list[Message]] = relationship("Message", back_populates="person")
    observations: Mapped[list[Observation]] = relationship("Observation", back_populates="person")
    episodes: Mapped[list[Episode]] = relationship("Episode", back_populates="person")
    reflections: Mapped[list[Reflection]] = relationship("Reflection", back_populates="person")
    user_portrait: Mapped[UserPortrait | None] = relationship(
        "UserPortrait", back_populates="person", uselist=False
    )
    emotion_records: Mapped[list[EmotionRecord]] = relationship(
        "EmotionRecord", back_populates="person"
    )
    interests: Mapped[list[Interest]] = relationship("Interest", back_populates="person")
    dialogue_plans: Mapped[list[DialoguePlan]] = relationship(
        "DialoguePlan", back_populates="person"
    )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    last_access_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="messages")
    observation: Mapped[Observation | None] = relationship(
        "Observation", back_populates="message", uselist=False
    )
    emotion_records: Mapped[list[EmotionRecord]] = relationship(
        "EmotionRecord", back_populates="message"
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="tag_message", back_populates="messages"
    )

    __table_args__ = (
        Index("message_embedding_idx", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

class Observation(Base):
    __tablename__ = "observation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    message_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("message.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    last_access_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="observations")
    message: Mapped[Message | None] = relationship("Message", back_populates="observation")
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="tag_observation", back_populates="observations"
    )

    __table_args__ = (
        Index("observation_embedding_idx", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


# ---------------------------------------------------------------------------
# Episode
# ---------------------------------------------------------------------------

class Episode(Base):
    __tablename__ = "episode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text)
    turning_point: Mapped[str | None] = mapped_column(Text)
    conclusion: Mapped[str | None] = mapped_column(Text)
    importance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    status: Mapped[EpisodeStatus] = mapped_column(
        Enum(EpisodeStatus, name="episode_status"),
        default=EpisodeStatus.ONGOING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="episodes")
    episode_messages: Mapped[list[EpisodeMessage]] = relationship(
        "EpisodeMessage", back_populates="episode"
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="tag_episode", back_populates="episodes"
    )

    __table_args__ = (
        Index("episode_embedding_idx", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class EpisodeMessage(Base):
    __tablename__ = "episode_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("episode.id"))
    message_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("message.id"))
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    episode: Mapped[Episode | None] = relationship("Episode", back_populates="episode_messages")
    message: Mapped[Message | None] = relationship("Message")


# ---------------------------------------------------------------------------
# Reflection
# ---------------------------------------------------------------------------

class Reflection(Base):
    __tablename__ = "reflection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("reflection.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    last_access_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="reflections")
    parent: Mapped[Reflection | None] = relationship(
        "Reflection", remote_side="Reflection.id", back_populates="children"
    )
    children: Mapped[list[Reflection]] = relationship(
        "Reflection", back_populates="parent"
    )
    sources: Mapped[list[ReflectionSource]] = relationship(
        "ReflectionSource", back_populates="reflection"
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="tag_reflection", back_populates="reflections"
    )

    __table_args__ = (
        Index("reflection_embedding_idx", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class ReflectionSource(Base):
    __tablename__ = "reflection_source"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reflection_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("reflection.id"))
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'message', 'observation', 'episode'
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    reflection: Mapped[Reflection | None] = relationship(
        "Reflection", back_populates="sources"
    )


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )

    # Relationships
    messages: Mapped[list[Message]] = relationship(
        "Message", secondary="tag_message", back_populates="tags"
    )
    observations: Mapped[list[Observation]] = relationship(
        "Observation", secondary="tag_observation", back_populates="tags"
    )
    reflections: Mapped[list[Reflection]] = relationship(
        "Reflection", secondary="tag_reflection", back_populates="tags"
    )
    episodes: Mapped[list[Episode]] = relationship(
        "Episode", secondary="tag_episode", back_populates="tags"
    )


class TagMessage(Base):
    __tablename__ = "tag_message"
    __table_args__ = (UniqueConstraint("tag_id", "message_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("message.id"), nullable=False)


class TagObservation(Base):
    __tablename__ = "tag_observation"
    __table_args__ = (UniqueConstraint("tag_id", "observation_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    observation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("observation.id"), nullable=False
    )


class TagReflection(Base):
    __tablename__ = "tag_reflection"
    __table_args__ = (UniqueConstraint("tag_id", "reflection_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    reflection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reflection.id"), nullable=False
    )


class TagEpisode(Base):
    __tablename__ = "tag_episode"
    __table_args__ = (UniqueConstraint("tag_id", "episode_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey("episode.id"), nullable=False)


# ---------------------------------------------------------------------------
# Emotion Record
# ---------------------------------------------------------------------------

class EmotionRecord(Base):
    __tablename__ = "emotion_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    message_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("message.id"))
    joy: Mapped[float] = mapped_column(Float, nullable=False)
    sadness: Mapped[float] = mapped_column(Float, nullable=False)
    anger: Mapped[float] = mapped_column(Float, nullable=False)
    surprise: Mapped[float] = mapped_column(Float, nullable=False)
    fear: Mapped[float] = mapped_column(Float, nullable=False)
    disgust: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'character'
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="emotion_records")
    message: Mapped[Message | None] = relationship("Message", back_populates="emotion_records")


# ---------------------------------------------------------------------------
# Interest
# ---------------------------------------------------------------------------

class Interest(Base):
    __tablename__ = "interest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    first_mentioned: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    last_mentioned: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="interests")


# ---------------------------------------------------------------------------
# Dialogue Plan
# ---------------------------------------------------------------------------

class DialoguePlan(Base):
    __tablename__ = "dialogue_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("person.id"))
    current_goal: Mapped[str] = mapped_column(Text, nullable=False)
    sub_goals: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    response_intention: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    person: Mapped[Person | None] = relationship("Person", back_populates="dialogue_plans")


# ---------------------------------------------------------------------------
# User Portrait
# ---------------------------------------------------------------------------

class UserPortrait(Base):
    __tablename__ = "user_portrait"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person.id"), unique=True, nullable=False
    )
    personality_traits: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    communication_style: Mapped[str | None] = mapped_column(Text)
    interests: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    # Relationships
    person: Mapped[Person] = relationship("Person", back_populates="user_portrait")


# ---------------------------------------------------------------------------
# Memory Access History
# ---------------------------------------------------------------------------

class MemoryAccessHistory(Base):
    __tablename__ = "memory_access_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'message', 'observation', 'reflection', 'episode'
    memory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    access_context: Mapped[str | None] = mapped_column(Text)
    reinforcement_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("memory_access_history_idx", "memory_type", "memory_id"),
    )
