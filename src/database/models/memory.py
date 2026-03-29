"""Memory-related ORM models: MemoryBase, Message, Observation, Episode, Reflection."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

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
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, EpisodeStatus

if TYPE_CHECKING:
    from database.models.emotion import EmotionHistory
    from database.models.participant import Participant


class MemoryBase(Base):
    """모든 기억 객체의 공통 속성 테이블."""

    __tablename__ = "memory_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("participant.id"), nullable=False
    )
    memory_type: Mapped[str] = mapped_column(Text, nullable=False)

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


class Message(Base):
    """원본 대화 메시지 테이블."""

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


class Observation(Base):
    """검색 최적화용 Observation 테이블."""

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


class Episode(Base):
    """의미 있는 대화 사건 묶음 테이블."""

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
        Enum(EpisodeStatus, name="episode_status", create_type=False),
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


class Reflection(Base):
    """원시 기억으로부터 추론된 상위 의미 테이블."""

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
    """Reflection과 원본 기억의 연결 테이블."""

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


class MemoryAccessLog(Base):
    """기억 접근 로그 테이블."""

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
